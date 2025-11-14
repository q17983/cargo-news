"""API routes for news sources management."""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, status
from uuid import UUID
from app.database.supabase_client import db
from app.database.models import NewsSource, NewsSourceCreate, NewsSourceUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_sources(active_only: bool = False):
    """
    Get all news sources with additional metadata about scraping configuration.
    """
    from app.scraper.scraper_factory import ScraperFactory
    
    try:
        sources = db.get_all_sources(active_only=active_only)
        
        # Enrich sources with scraper information
        enriched_sources = []
        for source in sources:
            source_dict = source.model_dump(mode='json')
            
            # Get the actual listing URL that will be scraped
            listing_url = ScraperFactory.get_listing_url(source.url)
            
            # Get which scraper will be used
            scraper = ScraperFactory.create_scraper(source.url)
            scraper_type = type(scraper).__name__
            
            # Get domain name for display
            from urllib.parse import urlparse
            parsed = urlparse(source.url)
            domain = parsed.netloc.replace('www.', '')
            
            source_dict['listing_url'] = listing_url
            source_dict['scraper_type'] = scraper_type
            source_dict['domain'] = domain
            source_dict['has_custom_scraper'] = scraper_type != 'BaseScraper'
            
            enriched_sources.append(source_dict)
            scraper.close()
        
        return enriched_sources
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sources: {str(e)}"
        )


@router.get("/{source_id}", response_model=NewsSource)
async def get_source(source_id: UUID):
    """Get a specific news source by ID."""
    source = db.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    return source


@router.post("", response_model=NewsSource, status_code=status.HTTP_201_CREATED)
async def create_source(
    source: NewsSourceCreate, 
    background_tasks: BackgroundTasks,
    auto_scrape: bool = Query(False, description="Automatically trigger scraping after creating source")
):
    """
    Create a new news source.
    
    Args:
        source: Source data (url, name, etc.)
        background_tasks: FastAPI background tasks
        auto_scrape: If True, automatically trigger scraping after creation
    """
    try:
        created_source = db.create_source(source)
        
        # Log which scraper will be used
        from app.scraper.scraper_factory import ScraperFactory
        scraper = ScraperFactory.create_scraper(created_source.url)
        scraper_type = type(scraper).__name__
        logger.info(f"Created source {created_source.id}: {created_source.url} (will use {scraper_type})")
        
        # Optionally trigger scraping automatically
        if auto_scrape and created_source.is_active:
            from app.api.routes.scrape import scrape_source
            background_tasks.add_task(scrape_source, created_source.id)
            logger.info(f"Auto-scraping triggered for new source: {created_source.name}")
        
        return created_source
    except Exception as e:
        logger.error(f"Error creating source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating source: {str(e)}"
        )


@router.put("/{source_id}", response_model=NewsSource)
async def update_source(source_id: UUID, update: NewsSourceUpdate):
    """Update a news source."""
    # Check if source exists
    existing_source = db.get_source(source_id)
    if not existing_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    try:
        updated_source = db.update_source(source_id, update)
        if not updated_source:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating source"
            )
        return updated_source
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating source: {str(e)}"
        )


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: UUID):
    """Delete a news source."""
    # Check if source exists
    existing_source = db.get_source(source_id)
    if not existing_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    success = db.delete_source(source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting source"
        )


@router.post("/{source_id}/test")
async def test_source(source_id: UUID):
    """Test scraping configuration for a source."""
    from app.scraper.scraper_factory import ScraperFactory
    
    source = db.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    scraper = None
    try:
        # Create scraper - factory automatically selects the right one
        scraper = ScraperFactory.create_scraper(source.url, delay_seconds=3, max_retries=2)
        scraper_type = type(scraper).__name__
        
        # Get the listing URL (factory handles URL transformation)
        listing_url = ScraperFactory.get_listing_url(source.url)
        
        logger.info(f"Testing source {source_id}: {source.url}")
        logger.info(f"Using scraper: {scraper_type}")
        logger.info(f"Listing URL: {listing_url}")
        
        # Try to fetch the listing page
        # Use asyncio executor to avoid blocking the event loop
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            soup = await asyncio.wait_for(
                loop.run_in_executor(None, scraper.fetch_page, listing_url),
                timeout=45.0
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {listing_url}")
            soup = None
        except Exception as e:
            logger.error(f"Error in async fetch: {str(e)}")
            soup = scraper.fetch_page(listing_url)
        
        if not soup:
            # Try the original URL as fallback
            logger.warning(f"Failed to fetch listing URL, trying original URL: {source.url}")
            try:
                soup = await asyncio.wait_for(
                    loop.run_in_executor(None, scraper.fetch_page, source.url),
                    timeout=45.0
                )
            except (asyncio.TimeoutError, Exception) as e:
                logger.error(f"Error fetching original URL: {str(e)}")
                soup = scraper.fetch_page(source.url)
                
            if not soup:
                return {
                    "success": False,
                    "message": "Failed to fetch the source page. The website may be blocking automated requests. The scraper will automatically use Playwright (browser automation) as a fallback during actual scraping.",
                    "scraper_used": scraper_type,
                    "listing_url_tried": listing_url,
                    "original_url": source.url,
                    "note": "This test uses basic HTTP requests. Actual scraping will use Playwright if requests fail, which is more robust against blocking."
                }
        
        # Try to extract article URLs if scraper supports it
        if hasattr(scraper, 'get_article_urls'):
            try:
                # Run in executor to avoid blocking
                urls = await asyncio.wait_for(
                    loop.run_in_executor(None, scraper.get_article_urls, listing_url, 1),
                    timeout=60.0
                )
                return {
                    "success": True,
                    "message": f"Successfully connected! Found {len(urls)} articles on first page.",
                    "articles_found": len(urls),
                    "scraper_used": scraper_type,
                    "listing_url": listing_url,
                    "sample_urls": urls[:3] if urls else []
                }
            except Exception as e:
                logger.error(f"Error extracting article URLs: {str(e)}")
                return {
                    "success": True,
                    "message": f"Connected to source but error extracting articles: {str(e)}",
                    "scraper_used": scraper_type
                }
        else:
            # Generic scraper - just confirm connection
            return {
                "success": True,
                "message": "Successfully connected to source. Note: This site may need a custom scraper for best results.",
                "scraper_used": scraper_type,
                "note": "Consider creating a custom scraper for this site (see app/scraper/README.md)"
            }
            
    except Exception as e:
        logger.error(f"Error testing source: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error testing source: {str(e)}",
            "scraper_used": type(scraper).__name__ if scraper else "Unknown"
        }
    finally:
        if scraper:
            scraper.close()

