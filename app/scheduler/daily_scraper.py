"""Scheduler for daily article scraping."""
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.database.supabase_client import db
from app.api.routes.scrape import scrape_source
from app.scraper.standalone_runner import run_standalone_scraper

logger = logging.getLogger(__name__)

scheduler = None


def _is_aircargonews(url: str) -> bool:
    return "aircargonews.net" in url.lower()


def _is_aircargoweek(url: str) -> bool:
    return "aircargoweek.com" in url.lower()


async def daily_scrape_job():
    """Job to scrape all active sources daily."""
    logger.info("Starting daily scrape job")

    try:
        sources = db.get_all_sources(active_only=True)

        if not sources:
            logger.info("No active sources found for daily scraping")
            return

        logger.info("Found %s active sources to scrape", len(sources))

        for source in sources:
            try:
                logger.info("Scraping source: %s (%s)", source.name, source.url)

                if _is_aircargonews(source.url):
                    # Use the same standalone script as local runs (all 16 categories).
                    await run_standalone_scraper(
                        source.id,
                        "scrape_aircargonews.py",
                        max_pages=settings.aircargonews_daily_max_pages,
                    )
                elif _is_aircargoweek(source.url):
                    await run_standalone_scraper(
                        source.id,
                        "scrape_aircargoweek.py",
                        max_pages=5,
                    )
                else:
                    await scrape_source(source.id)

            except Exception as e:
                logger.error("Error scraping source %s: %s", source.id, e)
                continue

        logger.info("Daily scrape job completed")

    except Exception as e:
        logger.error("Error in daily scrape job: %s", e)


def start_scheduler():
    """Start APScheduler with daily morning scrape (default 00:00 UTC = 08:00 HKT)."""
    global scheduler

    if scheduler and scheduler.running:
        logger.warning("Scheduler is already running")
        return

    try:
        hour = int(os.environ.get("SCRAPE_CRON_HOUR", settings.scrape_cron_hour))
        minute = int(os.environ.get("SCRAPE_CRON_MINUTE", settings.scrape_cron_minute))
        tz = os.environ.get("SCRAPE_CRON_TIMEZONE", settings.scrape_cron_timezone)

        scheduler = AsyncIOScheduler()

        scheduler.add_job(
            daily_scrape_job,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
            id="daily_scrape",
            name=f"Daily article scraping at {hour:02d}:{minute:02d} {tz}",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(
            "Scheduler started. Daily scraping at %02d:%02d %s (Air Cargo News uses scrape_aircargonews.py)",
            hour,
            minute,
            tz,
        )

    except Exception as e:
        logger.error("Error starting scheduler: %s", e)
        raise


def stop_scheduler():
    """Stop the scheduler."""
    global scheduler

    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    else:
        logger.warning("Scheduler is not running")
