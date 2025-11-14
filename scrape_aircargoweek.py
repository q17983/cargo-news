#!/usr/bin/env python3
"""
Complete scraping script for aircargoweek.com
This script will:
1. Scrape articles from aircargoweek.com
2. Generate AI summaries using Gemini
3. Save to Supabase database
4. Can be viewed in the web interface

Run from project root: python3 scrape_aircargoweek.py

IMPORTANT: Make sure to activate the virtual environment first!
    source venv/bin/activate
    python3 scrape_aircargoweek.py
"""
import sys
import os

# Get project root first
project_root = os.path.dirname(os.path.abspath(__file__))

# Check if running in virtual environment, if not, try to use venv Python
venv_python = os.path.join(project_root, 'venv', 'bin', 'python3')
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    # Not in venv, check if venv exists and use it
    if os.path.exists(venv_python):
        print("=" * 70)
        print("⚠️  Not in virtual environment. Switching to venv Python...")
        print("=" * 70)
        print()
        # Re-execute with venv Python
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print("=" * 70)
        print("⚠️  WARNING: Virtual environment not found!")
        print("=" * 70)
        print()
        print("Please create and activate the virtual environment first:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)

# Add project root to Python path
sys.path.insert(0, project_root)

import logging
from uuid import UUID
from app.scraper.scraper_factory import ScraperFactory
from app.scraper.aircargoweek_scraper import AircargoweekScraper
from app.ai.summarizer import Summarizer
from app.database.supabase_client import db
from app.database.models import ArticleCreate, ScrapingLogCreate, NewsSourceCreate

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_or_create_source():
    """Get or create the aircargoweek source in database."""
    source_url = "https://aircargoweek.com/news/"
    
    # Try to find existing source
    all_sources = db.get_all_sources(active_only=False)
    for source in all_sources:
        if 'aircargoweek.com' in source.url.lower():
            logger.info(f"Found existing source: {source.id} - {source.name}")
            return source
    
    # Create new source if not found
    logger.info("Creating new source for aircargoweek.com")
    source_data = NewsSourceCreate(
        url=source_url,
        name="Air Cargo Week",
        is_active=True
    )
    source = db.create_source(source_data)
    logger.info(f"Created new source: {source.id}")
    return source


def scrape_aircargoweek(max_pages=3, check_duplicates=True):
    """
    Complete scraping workflow for aircargoweek.com
    
    Args:
        max_pages: Maximum number of "Load more" clicks (default: 3 for daily scraping)
        check_duplicates: Whether to check for duplicates and stop early
    """
    print("=" * 70)
    print("Air Cargo Week - Complete Scraping Workflow")
    print("=" * 70)
    print()
    
    scraper = None
    articles_found = 0
    articles_processed = 0
    articles_failed = 0
    
    try:
        # Get or create source
        source = get_or_create_source()
        source_id = source.id
        
        logger.info(f"Starting scrape for source: {source.name} ({source.url})")
        print(f"Source: {source.name}")
        print(f"Source ID: {source_id}")
        print()
        
        # Create scraper
        scraper = ScraperFactory.create_scraper(
            source.url,
            delay_seconds=2,
            max_retries=3
        )
        
        # Get listing URL
        listing_url = ScraperFactory.get_listing_url(source.url)
        print(f"Listing URL: {listing_url}")
        print()
        
        # Check if this is first-time scraping
        existing_articles = db.get_articles_by_source(source_id, limit=1)
        is_first_scrape = len(existing_articles) == 0
        
        if is_first_scrape:
            print("⚠️  First-time scrape detected - will scrape more pages")
            max_pages = 5  # Reduced to 5 pages to prevent quota exhaustion
            check_duplicates = False
        else:
            print(f"📅 Daily scrape - will scrape up to {max_pages} pages")
            print(f"   (Stopping early if duplicates found)")
        
        print()
        print("Step 1: Extracting article URLs...")
        print("-" * 70)
        
        # Get article URLs
        if hasattr(scraper, 'get_article_urls'):
            duplicate_check = db.article_exists if check_duplicates else None
            article_urls = scraper.get_article_urls(
                listing_url,
                max_pages=max_pages,
                check_duplicates=check_duplicates,
                duplicate_check_func=duplicate_check
            )
            articles_found = len(article_urls)
        else:
            logger.warning("Scraper doesn't support get_article_urls")
            article_urls = []
        
        print(f"✓ Found {articles_found} article URLs")
        print()
        
        if articles_found == 0:
            print("⚠️  No articles found. Possible reasons:")
            print("   - All articles are already in database (duplicates)")
            print("   - Website structure changed")
            print("   - Network/blocking issues")
            return
        
        print(f"Step 2: Processing {len(article_urls)} articles...")
        print("-" * 70)
        print()
        
        # Initialize summarizer
        summarizer = Summarizer()
        
        # Process each article
        for idx, article_url in enumerate(article_urls, 1):
            try:
                print(f"[{idx}/{len(article_urls)}] Processing: {article_url[:60]}...")
                
                # Check if article already exists
                if db.article_exists(article_url):
                    print(f"   ⏭️  Already exists (skipping)")
                    continue
                
                # Scrape article
                article_data = scraper.scrape_article(article_url)
                if not article_data:
                    # Check if it's a 403 error (IP blocked)
                    # The scraper will log the 403 error, but we should inform the user
                    print(f"   ❌ Failed to scrape")
                    print(f"      (Check logs for details - might be 403 IP block)")
                    articles_failed += 1
                    continue
                
                # Check by title after scraping
                article_title = article_data.get('title', '')
                if db.article_exists(article_url, title=article_title):
                    print(f"   ⏭️  Already exists (by title)")
                    continue
                
                # Generate summary (with quota error handling)
                print(f"   🤖 Generating AI summary...")
                try:
                    summary_data = summarizer.summarize(
                        article_content=article_data.get('content', ''),
                        article_url=article_url,
                        article_title=article_data.get('title', ''),
                        article_date=article_data.get('published_date'),
                        source_name=source.name or "Air Cargo Week"
                    )
                except Exception as summary_error:
                    error_str = str(summary_error).lower()
                    if 'quota' in error_str or '429' in error_str:
                        print(f"\n⚠️  QUOTA EXCEEDED!")
                        print(f"   Processed {articles_processed} articles before hitting quota limit")
                        print(f"   Please wait 24 hours for quota reset or upgrade your API plan")
                        print(f"\n   Error: {str(summary_error)}")
                        return  # Stop processing
                    else:
                        raise  # Re-raise other errors
                
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
                print(f"   ✓ Saved to database")
                print()
                
            except Exception as e:
                logger.error(f"Error processing article {article_url}: {str(e)}")
                print(f"   ❌ Error: {str(e)}")
                articles_failed += 1
                continue
        
        # Log success
        status = 'success' if articles_failed == 0 else 'partial'
        log = ScrapingLogCreate(
            source_id=source_id,
            status=status,
            articles_found=articles_found
        )
        db.create_scraping_log(log)
        
        print()
        print("=" * 70)
        print("Scraping Complete!")
        print("=" * 70)
        print(f"Articles found:     {articles_found}")
        print(f"Articles processed: {articles_processed}")
        print(f"Articles failed:    {articles_failed}")
        print()
        print(f"✓ View articles at: http://localhost:3000 (or your frontend URL)")
        print()
        
    except Exception as e:
        logger.error(f"Error in scraping workflow: {str(e)}", exc_info=True)
        print()
        print("=" * 70)
        print("❌ Error occurred!")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print()
        
        # Log failure
        if 'source_id' in locals():
            log = ScrapingLogCreate(
                source_id=source_id,
                status='failed',
                error_message=str(e),
                articles_found=articles_found
            )
            db.create_scraping_log(log)
    
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape aircargoweek.com and save to Supabase')
    parser.add_argument('--max-pages', type=int, default=3,
                        help='Maximum number of "Load more" clicks (default: 3)')
    parser.add_argument('--no-duplicate-check', action='store_true',
                        help='Disable duplicate checking (scrape all articles)')
    
    args = parser.parse_args()
    
    scrape_aircargoweek(
        max_pages=args.max_pages,
        check_duplicates=not args.no_duplicate_check
    )

