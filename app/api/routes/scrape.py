"""API routes for manual scraping triggers."""
import logging
import asyncio
import subprocess
import sys
import os
from typing import List
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError as FutureTimeoutError
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from uuid import UUID
from app.database.supabase_client import db
from app.scraper.scraper_factory import ScraperFactory
from app.ai.summarizer import Summarizer
from app.database.models import ArticleCreate, ScrapingLogCreate
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Use ThreadPoolExecutor but with better handling for Playwright
# Note: ProcessPoolExecutor won't work because database connections aren't picklable
# Instead, we'll use ThreadPoolExecutor with proper error handling and timeouts
SCRAPING_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="scraper")

# Track running scraping tasks
# Format: {source_id: {"task": task, "process": process, "started_at": datetime}}
RUNNING_TASKS = {}


def _scrape_source_sync(source_id: UUID):
    """
    Synchronous scraping function that runs in background thread.
    This handles all the blocking I/O operations (Playwright, requests, etc.)
    """
    source = db.get_source(source_id)
    if not source:
        logger.error(f"Source {source_id} not found")
        return
    
    if not source.is_active:
        logger.info(f"Source {source_id} is not active, skipping")
        return
    
    scraper = None
    articles_found = 0  # Total URLs found
    articles_processed = 0  # Successfully saved (not duplicates)
    articles_failed = 0
    error_message = None
    
    try:
        logger.info(f"Starting scrape for source: {source.name} ({source.url})")
        
        # Create scraper
        scraper = ScraperFactory.create_scraper(
            source.url,
            delay_seconds=2,
            max_retries=3
        )
        
        # Get listing URL
        listing_url = ScraperFactory.get_listing_url(source.url)
        
        # Check if this is first-time scraping (no articles exist for this source)
        existing_articles = db.get_articles_by_source(source_id, limit=1)
        is_first_scrape = len(existing_articles) == 0
        
        # Determine max pages based on whether this is first scrape
        # IMPORTANT: Reduced first-time scrape to prevent quota issues
        if is_first_scrape:
            max_pages = 5  # Reduced to 5 pages to prevent quota exhaustion
            check_duplicates = True  # Always check duplicates to avoid re-processing
            logger.info(f"First-time scrape for {source.name}: will scrape up to {max_pages} pages (reduced to prevent quota issues)")
        else:
            max_pages = 3  # Daily: only scrape first few pages (10-15 articles per day)
            check_duplicates = True  # Check duplicates and stop early
            logger.info(f"Daily scrape for {source.name}: will scrape up to {max_pages} pages, stopping early on duplicates")
        
        # Get article URLs with smart duplicate checking
        if hasattr(scraper, 'get_article_urls'):
            # Pass duplicate check function if doing daily scrape
            duplicate_check = db.article_exists if check_duplicates else None
            article_urls = scraper.get_article_urls(
                listing_url, 
                max_pages=max_pages,
                check_duplicates=check_duplicates,
                duplicate_check_func=duplicate_check
            )
            articles_found = len(article_urls)  # Track total URLs found
        else:
            logger.warning(f"Scraper for {source.url} doesn't support get_article_urls")
            article_urls = []
        
        logger.info(f"Found {articles_found} article URLs, processing {len(article_urls)} new articles")
        
        # Initialize summarizer
        summarizer = Summarizer()
        
        # Process each article
        for article_url in article_urls:
            try:
                # Check if article already exists (by URL first, before scraping)
                if db.article_exists(article_url):
                    logger.info(f"Article already exists (by URL): {article_url}")
                    continue
                
                # Scrape article
                article_data = scraper.scrape_article(article_url)
                if not article_data:
                    articles_failed += 1
                    continue
                
                # Double-check by title after scraping (in case URL format changed)
                article_title = article_data.get('title', '')
                if db.article_exists(article_url, title=article_title):
                    logger.info(f"Article already exists (by title): {article_title[:50]}...")
                    continue
                
                # Generate summary (with quota error handling)
                try:
                    summary_data = summarizer.summarize(
                        article_content=article_data.get('content', ''),
                        article_url=article_url,
                        article_title=article_data.get('title', ''),
                        article_date=article_data.get('published_date'),
                        source_name=source.name or "Air Cargo News"
                    )
                except Exception as summary_error:
                    error_str = str(summary_error).lower()
                    if 'quota' in error_str or '429' in error_str:
                        logger.error(f"⚠️  QUOTA EXCEEDED - Stopping scraping to prevent further API calls")
                        logger.error(f"Processed {articles_processed} articles before quota limit")
                        error_message = f"Gemini API quota exceeded after processing {articles_processed} articles. Please wait or upgrade your API plan."
                        # Log partial success
                        log = ScrapingLogCreate(
                            source_id=source_id,
                            status='partial',
                            error_message=error_message,
                            articles_found=articles_found
                        )
                        db.create_scraping_log(log)
                        return  # Stop processing to avoid more quota errors
                    else:
                        # Re-raise other errors
                        raise
                
                # Create article record
                article = ArticleCreate(
                    source_id=source_id,
                    title=summary_data.get('translated_title', article_data.get('title', '')),
                    url=article_url,
                    content=article_data.get('content'),
                    summary=summary_data.get('summary', ''),
                    tags=summary_data.get('tags', []),
                    published_date=article_data.get('published_date')
                )
                
                db.create_article(article)
                articles_processed += 1
                logger.info(f"Processed article {articles_processed}: {article_url}")
                
            except Exception as e:
                logger.error(f"Error processing article {article_url}: {str(e)}")
                articles_failed += 1
                continue
        
        # Log success
        status = 'success' if articles_failed == 0 else 'partial'
        log = ScrapingLogCreate(
            source_id=source_id,
            status=status,
            articles_found=articles_found  # Total URLs found (not just processed)
        )
        db.create_scraping_log(log)
        
        logger.info(f"Scraping completed for {source.name}: {articles_found} URLs found, {articles_processed} articles processed, {articles_failed} failed")
        
    except Exception as e:
        logger.error(f"Error scraping source {source_id}: {str(e)}")
        error_message = str(e)
        
        # Log failure
        log = ScrapingLogCreate(
            source_id=source_id,
            status='failed',
            error_message=error_message,
            articles_found=articles_found  # Total URLs found (not just processed)
        )
        db.create_scraping_log(log)
    
    finally:
        if scraper:
            scraper.close()


async def scrape_source(source_id: UUID):
    """
    Async wrapper for scraping that runs the blocking operations in a thread pool.
    This ensures the FastAPI event loop is not blocked.
    
    IMPORTANT: For Air Cargo Week (Playwright), we run the standalone script as subprocess
    because Playwright has issues in threads. For other sources, we use thread pool.
    """
    # Check if this is Air Cargo Week (needs special handling for Playwright)
    source = db.get_source(source_id)
    if not source:
        logger.error(f"❌ Source {source_id} not found in database")
        raise HTTPException(status_code=404, detail="Source not found")
    
    logger.info(f"🔍 Checking source: {source.name} | URL: {source.url}")
    
    # Initialize RUNNING_TASKS entry for tracking (before starting any scraping)
    source_id_str = str(source_id)
    RUNNING_TASKS[source_id_str] = {
        "source_name": source.name,
        "started_at": datetime.now(),
        "status": "running"
    }
    logger.info(f"✅ Initialized RUNNING_TASKS entry for {source_id_str}: {list(RUNNING_TASKS.keys())}")
    
    # Check if this is Air Cargo Week (needs special handling for Playwright)
    if 'aircargoweek.com' in source.url.lower():
        # For Air Cargo Week, run standalone script as subprocess
        # This avoids Playwright threading issues
        logger.info(f"✅ Detected Air Cargo Week source - Using subprocess (Playwright compatibility)")
        logger.info(f"   Source ID: {source_id}")
        logger.info(f"   Source URL: {source.url}")
        logger.info(f"   RUNNING_TASKS entry exists: {source_id_str in RUNNING_TASKS}")
        try:
            result = await _scrape_via_subprocess(source_id)
            if result is None:
                logger.error(f"❌ Subprocess returned None - scraping failed to start for {source_id}")
                # Error already logged in _scrape_via_subprocess
        except Exception as e:
            logger.error(f"❌ Exception in scrape_source for Air Cargo Week: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Re-raise to be caught by outer handler if needed
            raise
        finally:
            # DO NOT clean up RUNNING_TASKS entry here!
            # The entry must persist until the process actually finishes
            # Cleanup happens when:
            # 1. Process completes (in the process.communicate() handler)
            # 2. Process times out (in the TimeoutError handler)
            # 3. User explicitly stops it (in stop_scraping endpoint)
            source_id_str = str(source_id)
            logger.info(f"🔍 scrape_source finally block for Air Cargo Week: {source_id_str}")
            logger.info(f"   RUNNING_TASKS entry exists: {source_id_str in RUNNING_TASKS}")
            if source_id_str in RUNNING_TASKS:
                task_info = RUNNING_TASKS[source_id_str]
                if "process" in task_info:
                    process = task_info["process"]
                    if process.returncode is None:
                        logger.info(f"⏸️  Process still running - keeping RUNNING_TASKS entry for {source_id_str}")
                        # Don't delete - process is still running!
                    else:
                        logger.info(f"✅ Process finished (returncode: {process.returncode}) - will clean up entry for {source_id_str}")
                        # Process finished, safe to clean up
                        del RUNNING_TASKS[source_id_str]
                else:
                    logger.warning(f"⚠️  No process in RUNNING_TASKS entry for {source_id_str} - cleaning up")
                    # No process stored, safe to clean up
                    del RUNNING_TASKS[source_id_str]
            else:
                logger.warning(f"⚠️  RUNNING_TASKS entry for {source_id_str} not found (already cleaned up?)")
    else:
        # For other sources, use thread pool (works fine for non-Playwright scrapers)
        try:
            loop = asyncio.get_event_loop()
            task_future = loop.run_in_executor(SCRAPING_EXECUTOR, _scrape_source_sync, source_id)
            # Store task future in RUNNING_TASKS for cancellation
            RUNNING_TASKS[str(source_id)]["task"] = task_future
            
            await asyncio.wait_for(task_future, timeout=1800)  # 30 minutes timeout
        except asyncio.TimeoutError:
            logger.error(f"⚠️  Scraping for source {source_id} timed out after 30 minutes. It may have hung.")
            # Log the timeout
            try:
                source = db.get_source(source_id)
                log = ScrapingLogCreate(
                    source_id=source_id,
                    status='failed',
                    error_message="Scraping timed out after 30 minutes. The scraper may have hung.",
                    articles_found=0
                )
                db.create_scraping_log(log)
            except Exception as e:
                logger.error(f"Error logging timeout: {str(e)}")
        except Exception as e:
            logger.error(f"Error in scrape_source for {source_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            # Clean up RUNNING_TASKS entry after completion or failure
            source_id_str = str(source_id)
            if source_id_str in RUNNING_TASKS:
                logger.info(f"🧹 Cleaning up RUNNING_TASKS entry for {source_id_str} (thread pool)")
                del RUNNING_TASKS[source_id_str]
            else:
                logger.warning(f"⚠️  RUNNING_TASKS entry for {source_id_str} not found during cleanup (thread pool)")


async def _scrape_via_subprocess(source_id: UUID):
    """
    Run scraping via subprocess (for Playwright-based scrapers like Air Cargo Week).
    This avoids Playwright threading issues by running the standalone script.
    Returns the process object so it can be tracked and cancelled.
    """
    source_id_str = str(source_id)
    logger.info(f"🚀 Starting Air Cargo Week subprocess scraping for source: {source_id_str}")
    
    # CRITICAL: Ensure RUNNING_TASKS entry exists at the very start
    # This prevents any KeyError from happening later
    if source_id_str not in RUNNING_TASKS:
        logger.warning(f"⚠️  RUNNING_TASKS entry missing at start of _scrape_via_subprocess for {source_id_str}")
        logger.warning(f"   Current RUNNING_TASKS keys: {list(RUNNING_TASKS.keys())}")
        # Create entry immediately
        try:
            source = db.get_source(source_id)
            RUNNING_TASKS[source_id_str] = {
                "source_name": source.name if source else "Unknown",
                "started_at": datetime.now(),
                "status": "running"
            }
            logger.info(f"✅ Created RUNNING_TASKS entry at start for {source_id_str}")
        except Exception as e:
            logger.error(f"❌ Failed to get source info: {str(e)}")
            # Create minimal entry
            RUNNING_TASKS[source_id_str] = {
                "source_name": "Unknown",
                "started_at": datetime.now(),
                "status": "running"
            }
            logger.info(f"✅ Created minimal RUNNING_TASKS entry at start for {source_id_str}")
    else:
        logger.info(f"✅ RUNNING_TASKS entry exists at start for {source_id_str}")
    
    try:
        # Get the project root directory
        # On Railway: /app/app/api/routes/scrape.py -> script is at /app/scrape_aircargoweek.py
        # Locally: /Users/sai/Cargo News/app/api/routes/scrape.py -> script is at /Users/sai/Cargo News/scrape_aircargoweek.py
        current_file = os.path.abspath(__file__)
        logger.info(f"🔍 Current file location: {current_file}")
        
        # Priority 1: Check /app directly (Railway root) - this is the most reliable
        if os.path.exists('/app/scrape_aircargoweek.py'):
            script_path = '/app/scrape_aircargoweek.py'
            project_root = '/app'
            logger.info(f"✅ Found script at: {script_path} (Railway root - priority 1)")
        # Priority 2: If we're in /app/app/... structure, go to /app
        elif current_file.startswith('/app/app/'):
            script_path = '/app/scrape_aircargoweek.py'
            project_root = '/app'
            logger.info(f"✅ Using Railway root path: {script_path} (detected /app/app/ structure)")
        # Priority 3: Try going up 4 levels (local development)
        else:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            script_path = os.path.join(project_root, 'scrape_aircargoweek.py')
            if os.path.exists(script_path):
                logger.info(f"✅ Found script at: {script_path} (local development)")
            else:
                # Last resort: try /app anyway (in case we're on Railway but path detection failed)
                if os.path.exists('/app/scrape_aircargoweek.py'):
                    script_path = '/app/scrape_aircargoweek.py'
                    project_root = '/app'
                    logger.info(f"✅ Found script at: {script_path} (fallback to /app)")
                else:
                    # Error - script not found anywhere
                    logger.error(f"❌ Script not found. Tried:")
                    logger.error(f"   /app/scrape_aircargoweek.py (Railway root)")
                    logger.error(f"   {script_path} (local path)")
                    logger.error(f"   Current file: {current_file}")
                    logger.error(f"   Current working directory: {os.getcwd()}")
                    if os.path.exists('/app'):
                        try:
                            files_in_app = os.listdir('/app')
                            logger.error(f"   Files in /app: {files_in_app[:20]}")
                        except:
                            logger.error(f"   Could not list /app directory")
                    raise FileNotFoundError(f"Script not found. Tried: /app/scrape_aircargoweek.py, {script_path}")
        
        # Verify script exists before proceeding
        if not os.path.exists(script_path):
            logger.error(f"❌ Script path calculated but file doesn't exist: {script_path}")
            raise FileNotFoundError(f"Script not found at calculated path: {script_path}")
        
        # Get Python interpreter path
        # On Railway, use the system Python (usually at /opt/venv/bin/python or sys.executable)
        # On local, try venv first
        venv_python = os.path.join(project_root, 'venv', 'bin', 'python3')
        if os.path.exists(venv_python):
            python_cmd = venv_python
        elif os.path.exists('/opt/venv/bin/python'):
            # Railway Python path
            python_cmd = '/opt/venv/bin/python'
        else:
            python_cmd = sys.executable
        
        logger.info(f"Running Air Cargo Week scraper via subprocess: {python_cmd} {script_path}")
        
        # CRITICAL: Pass environment variables to subprocess
        # The subprocess needs access to GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, etc.
        subprocess_env = os.environ.copy()
        logger.info(f"Passing environment variables to subprocess (GEMINI_API_KEY present: {'GEMINI_API_KEY' in subprocess_env})")
        
        # Run the standalone script as subprocess
        # This runs in a completely separate process, avoiding threading issues
        # Note: Script uses --no-duplicate-check to DISABLE duplicate checking
        # We want duplicate checking enabled, so we don't pass that flag
        process = await asyncio.create_subprocess_exec(
            python_cmd,
            script_path,
            '--max-pages', '5',  # First-time scrape limit
            # Don't pass --no-duplicate-check, so duplicate checking is enabled by default
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_root,
            env=subprocess_env  # CRITICAL: Pass environment variables
        )
        
        # Store process in running tasks for cancellation
        # Ensure RUNNING_TASKS entry exists (it should be created in scrape_source before calling this function)
        source_id_str = str(source_id)
        logger.info(f"🔍 Checking RUNNING_TASKS for {source_id_str} before storing process")
        logger.info(f"   Current RUNNING_TASKS keys: {list(RUNNING_TASKS.keys())}")
        
        if source_id_str not in RUNNING_TASKS:
            logger.warning(f"⚠️  RUNNING_TASKS entry missing for {source_id_str}, creating it now")
            # Get source info to create entry
            try:
                source = db.get_source(source_id)
                RUNNING_TASKS[source_id_str] = {
                    "source_name": source.name if source else "Unknown",
                    "started_at": datetime.now(),
                    "status": "running"
                }
                logger.info(f"✅ Created RUNNING_TASKS entry for {source_id_str}")
            except Exception as e:
                logger.error(f"❌ Failed to get source info for {source_id_str}: {str(e)}")
                # Create minimal entry
                RUNNING_TASKS[source_id_str] = {
                    "source_name": "Unknown",
                    "started_at": datetime.now(),
                    "status": "running"
                }
                logger.info(f"✅ Created minimal RUNNING_TASKS entry for {source_id_str}")
        else:
            logger.info(f"✅ RUNNING_TASKS entry exists for {source_id_str}")
        
        # Double-check entry exists before accessing
        if source_id_str not in RUNNING_TASKS:
            raise RuntimeError(f"RUNNING_TASKS entry for {source_id_str} still missing after creation attempt")
        
        # Safely store the process
        try:
            RUNNING_TASKS[source_id_str]["process"] = process
            logger.info(f"✅ Successfully stored process in RUNNING_TASKS for {source_id_str}")
        except KeyError as ke:
            logger.error(f"❌ KeyError when storing process: {str(ke)}")
            logger.error(f"   RUNNING_TASKS keys: {list(RUNNING_TASKS.keys())}")
            logger.error(f"   Looking for: {source_id_str}")
            raise
        
        # Wait for completion with timeout (30 minutes)
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=1800  # 30 minutes
            )
            
            if process.returncode == 0:
                logger.info(f"✅ Air Cargo Week scraping completed successfully")
                # Also decode stdout to see script output
                if stdout:
                    stdout_text = stdout.decode('utf-8', errors='ignore')
                    logger.info(f"Script output (last 500 chars): {stdout_text[-500:]}")
                # Clean up RUNNING_TASKS entry after successful completion
                if source_id_str in RUNNING_TASKS:
                    logger.info(f"🧹 Cleaning up RUNNING_TASKS entry after successful completion for {source_id_str}")
                    del RUNNING_TASKS[source_id_str]
            else:
                error_output = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                stdout_output = stdout.decode('utf-8', errors='ignore') if stdout else ""
                
                logger.error(f"❌ Air Cargo Week scraping failed with return code {process.returncode}")
                logger.error(f"   Stderr: {error_output[:1000]}")
                if stdout_output:
                    logger.error(f"   Stdout: {stdout_output[-500:]}")
                
                # Log the failure with more details
                try:
                    source = db.get_source(source_id)
                    error_message = f"Subprocess failed (exit code {process.returncode}): {error_output[:300]}"
                    log = ScrapingLogCreate(
                        source_id=source_id,
                        status='failed',
                        error_message=error_message,
                        articles_found=0
                    )
                    db.create_scraping_log(log)
                except Exception as log_error:
                    logger.error(f"❌ Failed to log subprocess failure: {str(log_error)}")
                
                # Clean up RUNNING_TASKS entry after failure
                if source_id_str in RUNNING_TASKS:
                    logger.info(f"🧹 Cleaning up RUNNING_TASKS entry after failure for {source_id_str}")
                    del RUNNING_TASKS[source_id_str]
        
        except asyncio.TimeoutError:
            logger.error(f"⚠️  Air Cargo Week scraping timed out after 30 minutes")
            process.kill()
            await process.wait()
            
            # Log the timeout
            source = db.get_source(source_id)
            log = ScrapingLogCreate(
                source_id=source_id,
                status='failed',
                error_message="Scraping timed out after 30 minutes",
                articles_found=0
            )
            db.create_scraping_log(log)
            
            # Clean up RUNNING_TASKS entry after timeout
            if source_id_str in RUNNING_TASKS:
                logger.info(f"🧹 Cleaning up RUNNING_TASKS entry after timeout for {source_id_str}")
                del RUNNING_TASKS[source_id_str]
        
        return process
            
    except Exception as e:
        error_details = str(e)
        error_type = type(e).__name__
        import traceback
        full_traceback = traceback.format_exc()
        
        logger.error(f"❌ Error running subprocess for Air Cargo Week (source: {source_id_str})")
        logger.error(f"   Error type: {error_type}")
        logger.error(f"   Error message: {error_details}")
        logger.error(f"   Full traceback:\n{full_traceback}")
        
        # Log the error with detailed message
        try:
            source = db.get_source(source_id)
            error_message = f"Subprocess error ({error_type}): {error_details[:500]}"
            log = ScrapingLogCreate(
                source_id=source_id,
                status='failed',
                error_message=error_message,
                articles_found=0
            )
            db.create_scraping_log(log)
            logger.info(f"✅ Error logged to database for source {source_id_str}")
        except Exception as log_error:
            logger.error(f"❌ Failed to log error to database: {str(log_error)}")
        
        # Clean up RUNNING_TASKS entry on exception
        if source_id_str in RUNNING_TASKS:
            logger.info(f"🧹 Cleaning up RUNNING_TASKS entry after exception for {source_id_str}")
            del RUNNING_TASKS[source_id_str]
        
        # Return None if process creation failed
        return None


# IMPORTANT: Specific routes must come BEFORE the generic /{source_id} route
# FastAPI matches routes in order, so /stop/{source_id} would be matched by /{source_id} if it comes first

@router.post("/all")
async def trigger_scrape_all(background_tasks: BackgroundTasks):
    """Manually trigger scraping for all active sources."""
    sources = db.get_all_sources(active_only=True)
    
    if not sources:
        return {
            "message": "No active sources found",
            "sources_queued": 0
        }
    
    # Add scraping tasks for all sources
    for source in sources:
        background_tasks.add_task(scrape_source, source.id)
    
    return {
        "message": f"Scraping started for {len(sources)} active sources",
        "sources_queued": len(sources)
    }


@router.get("/running")
async def get_running_tasks():
    """Get list of currently running scraping tasks."""
    running = []
    for source_id, task_info in RUNNING_TASKS.items():
        running.append({
            "source_id": source_id,
            "source_name": task_info.get("source_name", "Unknown"),
            "started_at": task_info.get("started_at").isoformat() if task_info.get("started_at") else None,
            "status": task_info.get("status", "running")
        })
    return {
        "running_tasks": running,
        "count": len(running)
    }


@router.post("/stop-all")
async def stop_all_scraping():
    """Stop all running scraping tasks."""
    stopped = []
    source_ids = list(RUNNING_TASKS.keys())
    
    for source_id_str in source_ids:
        task_info = RUNNING_TASKS[source_id_str]
        
        # Try to cancel subprocess
        if "process" in task_info:
            process = task_info["process"]
            try:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
            except Exception as e:
                logger.error(f"Error stopping subprocess: {str(e)}")
        
        # Try to cancel thread pool task
        if "task" in task_info:
            task = task_info["task"]
            try:
                task.cancel()
            except Exception as e:
                logger.error(f"Error cancelling task: {str(e)}")
        
        stopped.append(source_id_str)
    
    # Clear all running tasks
    RUNNING_TASKS.clear()
    
    return {
        "message": f"Stopped {len(stopped)} running tasks",
        "stopped_tasks": stopped
    }


@router.post("/stop/{source_id}")
async def stop_scraping(source_id: UUID):
    """Stop a running scraping task."""
    source_id_str = str(source_id)
    
    if source_id_str not in RUNNING_TASKS:
        raise HTTPException(
            status_code=404,
            detail=f"No running task found for source {source_id}"
        )
    
    task_info = RUNNING_TASKS[source_id_str]
    
    # Try to cancel subprocess
    if "process" in task_info:
        process = task_info["process"]
        try:
            process.terminate()
            logger.info(f"Terminated subprocess for source {source_id}")
            # Wait a bit, then kill if still running
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
                logger.warning(f"Killed subprocess for source {source_id} (didn't terminate gracefully)")
        except Exception as e:
            logger.error(f"Error stopping subprocess: {str(e)}")
    
    # Try to cancel thread pool task
    if "task" in task_info:
        task = task_info["task"]
        try:
            task.cancel()
            logger.info(f"Cancelled thread task for source {source_id}")
        except Exception as e:
            logger.error(f"Error cancelling task: {str(e)}")
    
    # Remove from tracking
    del RUNNING_TASKS[source_id_str]
    
    return {
        "message": f"Stopped scraping for source {source_id}",
        "source_id": source_id_str
    }


@router.get("/status/{source_id}")
async def get_scraping_status(source_id: UUID):
    """Get the latest scraping status for a source."""
    try:
        logs = db.get_scraping_logs(source_id=source_id, limit=1)
        if logs:
            latest_log = logs[0]
            return {
                "source_id": str(source_id),
                "status": latest_log.status,
                "articles_found": latest_log.articles_found,
                "error_message": latest_log.error_message,
                "created_at": latest_log.created_at.isoformat() if hasattr(latest_log, 'created_at') else None
            }
        return {
            "source_id": str(source_id),
            "status": "never_scraped",
            "message": "No scraping logs found for this source"
        }
    except Exception as e:
        logger.error(f"Error getting scraping status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving scraping status: {str(e)}"
        )


@router.get("/logs/{source_id}")
async def get_scraping_logs(source_id: UUID, limit: int = 10):
    """Get scraping logs for a source."""
    try:
        logs = db.get_scraping_logs(source_id=source_id, limit=limit)
        return [{
            "id": str(log.id),
            "status": log.status,
            "articles_found": log.articles_found,
            "error_message": log.error_message,
            "created_at": log.created_at.isoformat() if hasattr(log, 'created_at') else None
        } for log in logs]
    except Exception as e:
        logger.error(f"Error getting scraping logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving scraping logs: {str(e)}"
        )


# Generic route must come LAST - it matches any UUID
@router.post("/{source_id}")
async def trigger_scrape(source_id: UUID, background_tasks: BackgroundTasks):
    """Manually trigger scraping for a specific source."""
    source = db.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Add scraping task to background
    background_tasks.add_task(scrape_source, source_id)
    
    return {
        "message": f"Scraping started for source: {source.name}",
        "source_id": str(source_id)
    }

