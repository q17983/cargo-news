"""Base scraper class with anti-bot measures."""
import time
import random
import requests
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base scraper with anti-bot measures and error handling."""
    
    # Rotating user agents to avoid detection
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, delay_seconds: int = 2, max_retries: int = 3):
        """
        Initialize the base scraper.
        
        Args:
            delay_seconds: Delay between requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """Generate headers with random user agent."""
        headers = {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        if referer:
            headers['Referer'] = referer
            
        return headers
    
    def _rate_limit(self):
        """Apply rate limiting with random jitter."""
        delay = self.delay_seconds + random.uniform(0, 1)
        time.sleep(delay)
    
    def fetch_page(self, url: str, referer: Optional[str] = None) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage and return BeautifulSoup object.
        Tries requests first, falls back to Playwright if available.
        
        Args:
            url: URL to fetch
            referer: Referer URL for headers
            
        Returns:
            BeautifulSoup object or None if failed
        """
        self._rate_limit()
        
        # First try with requests
        try:
            headers = self._get_headers(referer)
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if we got blocked
            if response.status_code == 403:
                logger.warning(f"Got 403 Forbidden for {url}. Trying Playwright fallback...")
                return self._fetch_with_playwright(url)
                
            if response.status_code == 429:
                logger.warning(f"Rate limited (429) for {url}. Waiting longer...")
                time.sleep(10)
                # Try Playwright as fallback
                return self._fetch_with_playwright(url)
                
            soup = BeautifulSoup(response.content, 'lxml')
            return soup
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching {url} with requests: {str(e)}. Trying Playwright fallback...")
            return self._fetch_with_playwright(url)
    
    def _fetch_with_playwright(self, url: str) -> Optional[BeautifulSoup]:
        """Fallback method using Playwright for sites that block requests."""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=random.choice(self.USER_AGENTS),
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                try:
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    content = page.content()
                    browser.close()
                    
                    soup = BeautifulSoup(content, 'lxml')
                    logger.info(f"Successfully fetched {url} using Playwright")
                    return soup
                except Exception as e:
                    logger.error(f"Playwright error for {url}: {str(e)}")
                    browser.close()
                    return None
        except ImportError:
            logger.warning("Playwright not installed. Install with: pip install playwright && playwright install")
            return None
        except Exception as e:
            logger.error(f"Error using Playwright for {url}: {str(e)}")
            return None
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text from soup using CSS selector.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector
            
        Returns:
            Extracted text or None
        """
        try:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        except Exception as e:
            logger.error(f"Error extracting text with selector {selector}: {str(e)}")
        return None
    
    def extract_all_text(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract all matching text from soup using CSS selector.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector
            
        Returns:
            List of extracted text
        """
        try:
            elements = soup.select(selector)
            return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
        except Exception as e:
            logger.error(f"Error extracting all text with selector {selector}: {str(e)}")
        return []
    
    def extract_links(self, soup: BeautifulSoup, base_url: str, selector: str = 'a') -> List[str]:
        """
        Extract all links from soup.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs
            selector: CSS selector for links
            
        Returns:
            List of absolute URLs
        """
        links = []
        try:
            from urllib.parse import urljoin, urlparse
            
            elements = soup.select(selector)
            for elem in elements:
                href = elem.get('href')
                if href:
                    absolute_url = urljoin(base_url, href)
                    # Validate URL
                    parsed = urlparse(absolute_url)
                    if parsed.scheme in ['http', 'https']:
                        links.append(absolute_url)
        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
        return links
    
    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()

