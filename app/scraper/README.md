# Adding New Scrapers for Different News Sources

This guide explains how to add a new scraper for a different news source.

## Overview

The scraper system uses a factory pattern. Each news source can have its own custom scraper that inherits from `BaseScraper` and implements site-specific logic.

## Step-by-Step Guide

### 1. Create a New Scraper Class

Create a new file in `app/scraper/` named `[sitename]_scraper.py`:

```python
"""Scraper for [Site Name]."""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from urllib.parse import urljoin, urlparse
from app.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class [SiteName]Scraper(BaseScraper):
    """Scraper for [site-url]."""
    
    BASE_URL = "https://www.example.com"
    
    def __init__(self, delay_seconds: int = 2, max_retries: int = 3):
        """Initialize the scraper."""
        super().__init__(delay_seconds, max_retries)
    
    def get_article_urls(self, listing_url: str, max_pages: int = 5) -> List[str]:
        """
        Extract article URLs from listing pages.
        
        Args:
            listing_url: URL of the listing page
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of article URLs
        """
        article_urls = []
        current_url = listing_url
        pages_scraped = 0
        
        while pages_scraped < max_pages and current_url:
            logger.info(f"Scraping page {pages_scraped + 1}: {current_url}")
            soup = self.fetch_page(current_url)
            
            if not soup:
                break
            
            # Extract article URLs from current page
            page_urls = self._extract_article_urls_from_page(soup, current_url)
            article_urls.extend(page_urls)
            
            # Find next page
            current_url = self._get_next_page_url(soup, current_url)
            pages_scraped += 1
        
        # Remove duplicates
        seen = set()
        unique_urls = []
        for url in article_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def _extract_article_urls_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article URLs from a listing page."""
        urls = []
        # Implement your site-specific logic here
        # Example: article_links = soup.select('a.article-link')
        return urls
    
    def _get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Find the next page URL."""
        # Implement pagination logic
        return None
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article.
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with article data or None if failed
        """
        logger.info(f"Scraping article: {url}")
        soup = self.fetch_page(url)
        
        if not soup:
            return None
        
        title = self._extract_title(soup)
        content = self._extract_content(soup)
        published_date = self._extract_date(soup, url)
        
        if not title or not content:
            return None
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'published_date': published_date,
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        # Implement title extraction
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content."""
        # Implement content extraction
        return None
    
    def _extract_date(self, soup: BeautifulSoup, url: str) -> Optional[datetime]:
        """Extract published date."""
        # Implement date extraction
        return None
```

### 2. Register the Scraper in Factory

Edit `app/scraper/scraper_factory.py`:

```python
from app.scraper.[sitename]_scraper import [SiteName]Scraper

class ScraperFactory:
    @staticmethod
    def create_scraper(url: str, delay_seconds: int = 2, max_retries: int = 3) -> BaseScraper:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if 'aircargonews.net' in domain:
            return AircargonewsScraper(delay_seconds, max_retries)
        
        # Add your new scraper here
        elif 'example.com' in domain:
            return [SiteName]Scraper(delay_seconds, max_retries)
        
        # Fallback to generic scraper
        return BaseScraper(delay_seconds, max_retries)
    
    @staticmethod
    def get_listing_url(url: str) -> str:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if 'aircargonews.net' in domain:
            return f"{parsed.scheme}://{parsed.netloc}/latest-news/31.more?navcode=28"
        
        # Add your site's listing URL logic
        elif 'example.com' in domain:
            return f"{parsed.scheme}://{parsed.netloc}/news"  # Adjust as needed
        
        return url
```

### 3. Testing Your Scraper

Test your scraper before using it in production:

```python
from app.scraper.scraper_factory import ScraperFactory

scraper = ScraperFactory.create_scraper('https://example.com')
listing_url = ScraperFactory.get_listing_url('https://example.com')
urls = scraper.get_article_urls(listing_url, max_pages=1)
print(f"Found {len(urls)} articles")

# Test scraping one article
if urls:
    article = scraper.scrape_article(urls[0])
    print(f"Title: {article.get('title')}")
    print(f"Content length: {len(article.get('content', ''))}")
```

## Tips for Different Sites

1. **Inspect the website structure**: Use browser DevTools to find CSS selectors
2. **Handle pagination**: Each site has different pagination patterns
3. **Extract dates carefully**: Dates can be in various formats
4. **Filter out non-article links**: Some sites mix article links with category/navigation links
5. **Respect rate limits**: Use appropriate delays between requests

## Example: Aircargonews.net Scraper

See `aircargonews_scraper.py` for a complete example of:
- Extracting article URLs from listing pages
- Handling pagination
- Extracting title, content, and date
- Filtering out related articles

