"""Aircargoweek.com specific scraper."""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from urllib.parse import urljoin, urlparse
from app.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class AircargoweekScraper(BaseScraper):
    """Scraper for aircargoweek.com."""
    
    BASE_URL = "https://aircargoweek.com"
    
    def __init__(self, delay_seconds: int = 2, max_retries: int = 3):
        """Initialize the aircargoweek.com scraper."""
        super().__init__(delay_seconds, max_retries)
    
    def get_article_urls(self, listing_url: str, max_pages: int = 5, check_duplicates: bool = False, duplicate_check_func = None) -> List[str]:
        """
        Extract article URLs from listing pages.
        Uses Playwright to handle JavaScript "Load more" button.
        
        Args:
            listing_url: URL of the listing page
            max_pages: Maximum number of "load more" clicks
            check_duplicates: If True, check for duplicates and stop early
            duplicate_check_func: Function to check if URL exists
            
        Returns:
            List of article URLs
        """
        article_urls = []
        consecutive_duplicate_loads = 0
        max_consecutive_duplicates = 2
        
        try:
            from playwright.sync_api import sync_playwright
            import random
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=random.choice(self.USER_AGENTS),
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                try:
                    response = page.goto(listing_url, wait_until='networkidle', timeout=30000)
                    
                    # Check for 403 Forbidden (IP blocked)
                    if response and response.status == 403:
                        logger.error(f"⚠️  403 FORBIDDEN - IP blocked by aircargoweek.com")
                        logger.error("   Your IP address has been blocked. Cannot scrape article URLs.")
                        logger.error("   Solutions: Wait 24-48 hours, use VPN/proxy, or different network")
                        browser.close()
                        return []
                    
                    # Check for other error status codes
                    if response and response.status >= 400:
                        logger.error(f"⚠️  HTTP {response.status} error loading listing page")
                        browser.close()
                        return []
                    
                    # Handle cookie consent if present
                    try:
                        accept_selectors = [
                            'button:has-text("Accept")',
                            'button:has-text("同意")',
                            '[id*="accept"]',
                            '[class*="accept"]',
                            'button[id*="cookie"]'
                        ]
                        for selector in accept_selectors:
                            try:
                                accept_button = page.query_selector(selector)
                                if accept_button and accept_button.is_visible():
                                    accept_button.click()
                                    page.wait_for_timeout(1000)
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    # Wait for page to fully load
                    page.wait_for_timeout(4000)
                    
                    # Wait for "All the news" section to appear
                    try:
                        # Look for text "All the news" or article listings
                        page.wait_for_selector('text="All the news", h2:has-text("All the news"), h3:has-text("All the news")', timeout=10000)
                    except:
                        logger.warning("'All the news' section not found, continuing anyway")
                    
                    # Scroll down to trigger lazy loading of articles
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                    page.wait_for_timeout(2000)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(3000)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(2000)
                    
                    # Extract articles from initial page
                    initial_urls = self._extract_article_urls_from_page_playwright(page)
                    article_urls.extend(initial_urls)
                    logger.info(f"Found {len(initial_urls)} articles on initial load")
                    
                    # Click "Load more" button multiple times
                    for load_count in range(max_pages):
                        # Check for duplicates if enabled
                        if check_duplicates and duplicate_check_func and article_urls:
                            new_urls = [url for url in article_urls if not duplicate_check_func(url)]
                            if len(new_urls) == 0:
                                consecutive_duplicate_loads += 1
                                if consecutive_duplicate_loads >= max_consecutive_duplicates:
                                    logger.info(f"Stopping early: Found {max_consecutive_duplicates} consecutive loads with all duplicates")
                                    break
                                consecutive_duplicate_loads = 0
                        
                        # Find and click "Load more" button
                        try:
                            load_more_selectors = [
                                'button:has-text("Load more")',
                                'a:has-text("Load more")',
                                'button:has-text("load more")',
                                'a:has-text("load more")',
                                '[class*="load-more"]',
                                '[id*="load-more"]',
                                '[class*="loadmore"]',
                                'button[class*="load"]',
                                'a[class*="load"]',
                            ]
                            
                            load_more_clicked = False
                            for selector in load_more_selectors:
                                try:
                                    button = page.query_selector(selector)
                                    if button and button.is_visible():
                                        logger.info(f"Clicking 'Load more' button (attempt {load_count + 1})")
                                        button.click()
                                        page.wait_for_timeout(4000)  # Wait for new content to load
                                        load_more_clicked = True
                                        break
                                except:
                                    continue
                            
                            if not load_more_clicked:
                                logger.info("No 'Load more' button found, stopping")
                                break
                            
                            # Extract new articles after loading
                            new_urls = self._extract_article_urls_from_page_playwright(page)
                            
                            # Filter out duplicates we already have
                            existing_set = set(article_urls)
                            unique_new = [url for url in new_urls if url not in existing_set]
                            
                            if unique_new:
                                article_urls.extend(unique_new)
                                logger.info(f"Load {load_count + 1}: Found {len(unique_new)} new articles (total: {len(article_urls)})")
                                consecutive_duplicate_loads = 0
                            else:
                                logger.info(f"Load {load_count + 1}: No new articles found")
                                consecutive_duplicate_loads += 1
                                if consecutive_duplicate_loads >= max_consecutive_duplicates:
                                    logger.info(f"Stopping early: {max_consecutive_duplicates} consecutive loads with no new articles")
                                    break
                            
                        except Exception as e:
                            logger.warning(f"Error clicking load more: {str(e)}")
                            break
                    
                    browser.close()
                    
                except Exception as e:
                    logger.error(f"Error in Playwright scraping: {str(e)}")
                    browser.close()
                    return []
        
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright && playwright install")
            return []
        except Exception as e:
            logger.error(f"Error getting article URLs: {str(e)}")
            return []
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in article_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Total unique articles found: {len(unique_urls)}")
        return unique_urls
    
    def _extract_article_urls_from_page_playwright(self, page) -> List[str]:
        """Extract article URLs from the current page using Playwright."""
        urls = []
        seen = set()
        
        try:
            # Simple approach: get ALL links and filter for article URLs
            # Article URLs are like: aircargoweek.com/article-title-slug/
            all_links = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(l => l.href).filter(href => 
                        href &&
                        href.includes('aircargoweek.com') &&
                        href !== 'https://aircargoweek.com/' &&
                        href !== 'https://aircargoweek.com/news/' &&
                        href !== 'https://aircargoweek.com/news' &&
                        !href.includes('#') &&
                        !href.includes('popup') &&
                        !href.includes('elementor-action')
                    );
                }
            """)
            
            for href in all_links:
                # Clean up URL
                absolute_url = urljoin(self.BASE_URL, href.split('#')[0].split('?')[0])
                parsed = urlparse(absolute_url)
                path_parts = [p for p in parsed.path.split('/') if p]
                
                # Filter for article URLs:
                # - Has slug (path parts > 0)
                # - Slug is long enough (> 10 chars) to be an article
                # - Not navigation pages
                if ('aircargoweek.com' in parsed.netloc and 
                    len(path_parts) >= 1 and 
                    len(path_parts[0]) > 10 and
                    absolute_url not in seen and
                    absolute_url != 'https://aircargoweek.com/' and
                    absolute_url != 'https://aircargoweek.com/news/' and
                    not any(nav in absolute_url.lower() for nav in [
                        '/features', '/publications', '/events', '/awards', 
                        '/about', '/contact', '/subscribe', '/home',
                        '/privacy', '/terms', '/cookies'
                    ])):
                    urls.append(absolute_url)
                    seen.add(absolute_url)
                    logger.debug(f"Found article URL: {absolute_url}")
            
            return urls
        
        except Exception as e:
            logger.error(f"Error extracting article URLs: {str(e)}")
            return []
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article.
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with article data or None if failed
        """
        logger.info(f"Scraping article: {url}")
        
        # Use Playwright since site blocks requests
        try:
            from playwright.sync_api import sync_playwright
            import random
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=random.choice(self.USER_AGENTS),
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                try:
                    # Use 'domcontentloaded' first, then wait for content
                    # 'networkidle' can hang if there are continuous network requests (analytics, etc.)
                    response = page.goto(url, wait_until='domcontentloaded', timeout=20000)
                    
                    # Check for 403 Forbidden (IP blocked)
                    if response and response.status == 403:
                        logger.error(f"⚠️  403 FORBIDDEN - IP blocked by aircargoweek.com for {url}")
                        logger.error("   Your IP address has been blocked. Solutions:")
                        logger.error("   1. Wait 24-48 hours for block to expire")
                        logger.error("   2. Use a VPN or proxy")
                        logger.error("   3. Use a different network/IP address")
                        browser.close()
                        return None
                    
                    # Check for other error status codes
                    if response and response.status >= 400:
                        logger.error(f"⚠️  HTTP {response.status} error for {url}")
                        browser.close()
                        return None
                    
                    # Wait for content to fully load (give JavaScript time to render)
                    page.wait_for_timeout(5000)
                    
                    # Wait for article content to be present (with timeout)
                    try:
                        page.wait_for_selector('h1, .entry-title, .post-title, .entry-content, .post-content', timeout=10000)
                    except:
                        logger.warning("Article heading/content not found immediately, continuing anyway")
                    
                    # Additional wait for JavaScript to fully render content
                    page.wait_for_timeout(2000)
                    
                    # Get content
                    content = page.content()
                    browser.close()
                    
                    soup = BeautifulSoup(content, 'lxml')
                    
                    title = self._extract_title(soup)
                    article_content = self._extract_content(soup)
                    published_date = self._extract_date(soup, url)
                    
                    if not title:
                        logger.warning(f"Failed to extract title from {url}")
                        return None
                    
                    if not article_content:
                        logger.warning(f"Failed to extract content from {url} (title found: {title[:50]}...)")
                        return None
                    
                    return {
                        'url': url,
                        'title': title,
                        'content': article_content,
                        'published_date': published_date,
                    }
                    
                except Exception as e:
                    logger.error(f"Error scraping article {url}: {str(e)}")
                    browser.close()
                    return None
        
        except ImportError:
            logger.error("Playwright not installed")
            return None
        except Exception as e:
            logger.error(f"Error in Playwright scraping: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        # Try multiple selectors for aircargoweek.com
        selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1',
            '.entry-title',
            '.post-title',
            'article h1',
            'main h1',
            '.elementor-heading-title',
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content."""
        # Try multiple content selectors (prioritize more specific ones)
        selectors = [
            '.entry-content',
            '.post-content',
            '.article-content',
            'article .content',
            '.elementor-widget-theme-post-content',
            '.elementor-post__content',
            'main article',
            'article',
            '.content',
        ]
        
        for selector in selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove script, style, nav, aside, footer, header
                for tag in content_elem(["script", "style", "nav", "aside", "footer", "header"]):
                    tag.decompose()
                
                # Remove title if in content
                h1_in_content = content_elem.select_one('h1')
                if h1_in_content:
                    h1_in_content.decompose()
                
                # Remove social shares, tags, author info, etc.
                for tag in content_elem.select('.social-share, .tags, .author, .post-meta, .elementor-share-buttons, .post-author, .entry-meta'):
                    tag.decompose()
                
                # Remove "Related Posts" or "More Articles" sections
                for tag in content_elem.select('.related-posts, .more-articles, .related-articles, .post-navigation'):
                    tag.decompose()
                
                text = content_elem.get_text(separator='\n', strip=True)
                
                # Filter out very short content (likely not the main article)
                if len(text) > 200:
                    # Additional validation: check if it looks like article content
                    # Article content should have multiple paragraphs
                    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
                    if len(paragraphs) >= 2:  # At least 2 substantial paragraphs
                        return text
                    elif len(text) > 500:  # Or if total text is long enough
                        return text
        
        # Fallback: try to extract from main or body if no specific content found
        main_elem = soup.select_one('main, body')
        if main_elem:
            # Remove all non-content elements
            for tag in main_elem(["script", "style", "nav", "aside", "footer", "header", "form"]):
                tag.decompose()
            
            # Remove common non-content sections
            for tag in main_elem.select('.sidebar, .widget, .navigation, .menu, .header, .footer'):
                tag.decompose()
            
            text = main_elem.get_text(separator='\n', strip=True)
            paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
            if len(paragraphs) >= 2 and len(text) > 200:
                return text
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup, url: str) -> Optional[datetime]:
        """Extract published date."""
        from dateutil import parser as date_parser
        
        # Try multiple date selectors
        selectors = [
            'time[datetime]',
            'time.published',
            '.published-date',
            '.post-date',
            '.entry-date',
            'time',
            '.date',
            '.elementor-post-info__item--type-date',
        ]
        
        for selector in selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                # Try datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    try:
                        return date_parser.parse(datetime_attr)
                    except:
                        pass
                
                # Try text content
                date_text = date_elem.get_text(strip=True)
                if date_text:
                    try:
                        return date_parser.parse(date_text)
                    except:
                        pass
        
        # Try to extract from page text (format: "November 12, 2025")
        try:
            page_text = soup.get_text()
            date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
            match = re.search(date_pattern, page_text)
            if match:
                try:
                    return date_parser.parse(match.group(0))
                except:
                    pass
        except:
            pass
        
        return None

