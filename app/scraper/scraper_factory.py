"""Factory for creating appropriate scrapers based on URL."""
import logging
from typing import Optional
from urllib.parse import urlparse
from app.scraper.base_scraper import BaseScraper
from app.scraper.aircargonews_scraper import AircargonewsScraper
from app.scraper.aircargoweek_scraper import AircargoweekScraper
from app.scraper.stattimes_scraper import StattimesScraper

logger = logging.getLogger(__name__)


class ScraperFactory:
    """Factory for creating site-specific scrapers."""
    
    @staticmethod
    def create_scraper(url: str, delay_seconds: int = 2, max_retries: int = 3) -> BaseScraper:
        """
        Create an appropriate scraper for the given URL.
        
        Args:
            url: URL to scrape
            delay_seconds: Delay between requests
            max_retries: Maximum retries
            
        Returns:
            Appropriate scraper instance
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Site-specific scrapers
        if 'aircargonews.net' in domain:
            logger.info(f"Using AircargonewsScraper for {url}")
            return AircargonewsScraper(delay_seconds, max_retries)
        
        if 'aircargoweek.com' in domain:
            logger.info(f"Using AircargoweekScraper for {url}")
            return AircargoweekScraper(delay_seconds, max_retries)
        
        if 'stattimes.com' in domain:
            logger.info(f"Using StattimesScraper for {url}")
            return StattimesScraper(delay_seconds, max_retries)
        
        # Add more site-specific scrapers here as needed
        # Example:
        # elif 'othernewsite.com' in domain:
        #     from app.scraper.othernewsite_scraper import OtherNewsiteScraper
        #     return OtherNewsiteScraper(delay_seconds, max_retries)
        
        # Fallback to generic scraper
        logger.info(f"Using BaseScraper (generic) for {url}")
        return BaseScraper(delay_seconds, max_retries)
    
    @staticmethod
    def get_listing_url(url: str) -> str:
        """
        Get the listing page URL for a news source.
        For aircargonews.net, use the latest-news page.
        
        Args:
            url: Source URL (could be homepage or specific section)
            
        Returns:
            Listing page URL
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if 'aircargonews.net' in domain:
            # Use the latest-news listing page which has all articles
            if '/latest-news' not in url:
                return f"{parsed.scheme}://{parsed.netloc}/latest-news/31.more?navcode=28"
            return url
        
        if 'aircargoweek.com' in domain:
            # Use the news listing page
            if '/news' not in url:
                return f"{parsed.scheme}://{parsed.netloc}/news/"
            return url
        
        if 'stattimes.com' in domain:
            # Use the latest-news listing page
            if '/latest-news' not in url:
                return f"{parsed.scheme}://{parsed.netloc}/latest-news"
            return url
        
        # For other sites, return as-is or implement logic
        # Example:
        # elif 'othernewsite.com' in domain:
        #     return f"{parsed.scheme}://{parsed.netloc}/news"  # Adjust to site's listing page
        
        return url

