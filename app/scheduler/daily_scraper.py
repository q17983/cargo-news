"""Scheduler for daily article scraping."""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database.supabase_client import db
from app.api.routes.scrape import scrape_source

logger = logging.getLogger(__name__)

scheduler = None


async def daily_scrape_job():
    """Job to scrape all active sources daily."""
    logger.info("Starting daily scrape job")
    
    try:
        # Get all active sources
        sources = db.get_all_sources(active_only=True)
        
        if not sources:
            logger.info("No active sources found for daily scraping")
            return
        
        logger.info(f"Found {len(sources)} active sources to scrape")
        
        # Scrape each source
        for source in sources:
            try:
                logger.info(f"Scraping source: {source.name} ({source.url})")
                await scrape_source(source.id)
            except Exception as e:
                logger.error(f"Error scraping source {source.id}: {str(e)}")
                continue
        
        logger.info("Daily scrape job completed")
        
    except Exception as e:
        logger.error(f"Error in daily scrape job: {str(e)}")


def start_scheduler():
    """Start the APScheduler with daily scraping at 00:00 UTC."""
    global scheduler
    
    if scheduler and scheduler.running:
        logger.warning("Scheduler is already running")
        return
    
    try:
        scheduler = AsyncIOScheduler()
        
        # Schedule daily scraping at 00:00 UTC
        scheduler.add_job(
            daily_scrape_job,
            trigger=CronTrigger(hour=0, minute=0, timezone='UTC'),
            id='daily_scrape',
            name='Daily article scraping at 00:00 UTC',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started. Daily scraping scheduled for 00:00 UTC")
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise


def stop_scheduler():
    """Stop the scheduler."""
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    else:
        logger.warning("Scheduler is not running")

