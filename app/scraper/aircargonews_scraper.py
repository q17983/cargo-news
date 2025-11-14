"""Aircargonews.net specific scraper."""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from urllib.parse import urljoin, urlparse
from app.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class AircargonewsScraper(BaseScraper):
    """Scraper for aircargonews.net."""
    
    BASE_URL = "https://www.aircargonews.net"
    
    # CSS selectors for aircargonews.net
    ARTICLE_LIST_SELECTOR = "article, .article-item, .news-item"
    ARTICLE_TITLE_SELECTOR = "h1, h2, .article-title, .title"
    ARTICLE_LINK_SELECTOR = "a"
    ARTICLE_CONTENT_SELECTOR = ".article-content, .content, .post-content, main article"
    ARTICLE_DATE_SELECTOR = "time, .date, .published-date, .article-date"
    PAGINATION_SELECTOR = ".pagination a, .next-page, a[rel='next']"
    
    def __init__(self, delay_seconds: int = 2, max_retries: int = 3):
        """Initialize the aircargonews.net scraper."""
        super().__init__(delay_seconds, max_retries)
    
    def get_article_urls(self, listing_url: str, max_pages: int = 5, check_duplicates: bool = False, duplicate_check_func = None) -> List[str]:
        """
        Extract article URLs from listing pages.
        Can stop early if encountering too many duplicates (for daily scraping).
        
        Args:
            listing_url: URL of the listing page
            max_pages: Maximum number of pages to scrape
            check_duplicates: If True, check for duplicates and stop early when finding too many
            duplicate_check_func: Function to check if URL exists (url) -> bool
            
        Returns:
            List of article URLs
        """
        article_urls = []
        current_url = listing_url
        pages_scraped = 0
        consecutive_duplicate_pages = 0
        max_consecutive_duplicates = 2  # Stop after 2 pages of all duplicates
        
        while pages_scraped < max_pages and current_url:
            logger.info(f"Scraping page {pages_scraped + 1}: {current_url}")
            soup = self.fetch_page(current_url)
            
            if not soup:
                logger.warning(f"Failed to fetch page: {current_url}")
                break
            
            # Extract article links from current page
            page_urls = self._extract_article_urls_from_page(soup, current_url)
            logger.info(f"Found {len(page_urls)} articles on page {pages_scraped + 1}")
            
            if not page_urls:
                logger.warning(f"No articles found on page {pages_scraped + 1}, stopping")
                break
            
            # If checking duplicates, filter out existing ones
            if check_duplicates and duplicate_check_func:
                new_urls = []
                duplicate_count = 0
                for url in page_urls:
                    if duplicate_check_func(url):
                        duplicate_count += 1
                    else:
                        new_urls.append(url)
                
                logger.info(f"Page {pages_scraped + 1}: {len(new_urls)} new articles, {duplicate_count} duplicates")
                
                # If all articles on this page are duplicates, increment counter
                if len(new_urls) == 0:
                    consecutive_duplicate_pages += 1
                    logger.info(f"All articles on page {pages_scraped + 1} are duplicates ({consecutive_duplicate_pages}/{max_consecutive_duplicates})")
                    
                    # Stop if we've hit too many consecutive duplicate pages
                    if consecutive_duplicate_pages >= max_consecutive_duplicates:
                        logger.info(f"Stopping early: Found {max_consecutive_duplicates} consecutive pages with all duplicates")
                        break
                else:
                    # Reset counter if we found new articles
                    consecutive_duplicate_pages = 0
                    article_urls.extend(new_urls)
            else:
                # No duplicate checking, add all URLs
                article_urls.extend(page_urls)
            
            # Find next page
            current_url = self._get_next_page_url(soup, current_url)
            pages_scraped += 1
            
            if not current_url:
                logger.info("No more pages found")
                break
        
        # Remove duplicates while preserving order (in case of any duplicates within pages)
        seen = set()
        unique_urls = []
        for url in article_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Total unique new articles found: {len(unique_urls)} (scraped {pages_scraped} pages)")
        return unique_urls
    
    def _extract_article_urls_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article URLs from a listing page."""
        urls = []
        seen = set()
        
        # Primary method: Look for links ending with .article (actual article pages)
        article_links = soup.select('a[href$=".article"]')
        for link in article_links:
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                if 'aircargonews.net' in parsed.netloc and absolute_url not in seen:
                    urls.append(absolute_url)
                    seen.add(absolute_url)
        
        # Secondary method: Look for article links in headings (h2, h3, h4)
        heading_links = soup.select('h2 a, h3 a, h4 a, .article-title a, .title a, .headline a')
        for link in heading_links:
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                # Check if it's an article URL (has .article or matches article pattern)
                if ('aircargonews.net' in parsed.netloc and 
                    ('.article' in absolute_url or 
                     (any(char.isdigit() for char in parsed.path.split('/')[-1]) and 
                      len(parsed.path.split('/')) >= 3)) and
                    absolute_url not in seen):
                    urls.append(absolute_url)
                    seen.add(absolute_url)
        
        # Filter out category pages (they don't have .article and are usually 1-2 path segments)
        filtered_urls = []
        for url in urls:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            # Article URLs typically have at least 2 path segments and end with .article or have numbers
            if '.article' in url or (len(path_parts) >= 2 and any(char.isdigit() for char in path_parts[-1])):
                filtered_urls.append(url)
        
        return filtered_urls
    
    def _get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Find the next page URL."""
        # For latest-news page, look for pagination with page parameter
        current_page_num = self._extract_page_number(current_url) or 1
        
        # Try to find "Next Page" link
        next_links = soup.select('a[href*="page="]')
        for link in next_links:
            text = link.get_text(strip=True).lower()
            if 'next' in text or '>' in text:
                href = link.get('href')
                if href:
                    return urljoin(current_url, href)
        
        # Look for the next page number link
        for link in next_links:
            href = link.get('href')
            if href:
                page_num = self._extract_page_number(href)
                if page_num and page_num == current_page_num + 1:
                    return urljoin(current_url, href)
        
        # For latest-news format, construct next page URL
        if '/latest-news' in current_url and 'page=' in current_url:
            next_page = current_page_num + 1
            if next_page <= 10:  # Limit to 10 pages as per user's note
                # Replace page parameter
                if '&page=' in current_url:
                    next_url = current_url.replace(f'&page={current_page_num}', f'&page={next_page}')
                elif '?page=' in current_url:
                    next_url = current_url.replace(f'?page={current_page_num}', f'?page={next_page}')
                else:
                    next_url = f"{current_url}&page={next_page}"
                return next_url
        
        return None
    
    def _extract_page_number(self, url: str) -> Optional[int]:
        """Extract page number from URL."""
        import re
        patterns = [
            r'page=(\d+)',
            r'/page/(\d+)',
            r'/p(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
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
            logger.error(f"Failed to fetch article: {url}")
            return None
        
        # Extract article data
        title = self._extract_title(soup)
        content = self._extract_content(soup)
        published_date = self._extract_date(soup, url)
        
        if not title or not content:
            logger.warning(f"Incomplete article data for {url}")
            return None
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'published_date': published_date,
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        # Try multiple selectors (prioritize h1)
        selectors = [
            'h1',
            'h1.article-title',
            '.article-title',
            '.title',
            'header h1',
            'main h1',
            '.headline',
        ]
        
        for selector in selectors:
            title = self.extract_text(soup, selector)
            if title and len(title) > 5:  # Reasonable title length
                return title.strip()
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content - only the main article, excluding related articles."""
        # Try multiple content selectors (prioritize aircargonews.net specific ones)
        selectors = [
            '.restrictedcontent',
            '.contentWrapper',
            'main',
            '.article-content',
            '.content',
            '.post-content',
            'main article',
            'article',
            '.entry-content',
            '.article-body',
            '.story-body',
        ]
        
        for selector in selectors:
            content_elem = soup.select_one(selector)
            if not content_elem:
                continue
            
            # For .restrictedcontent, we need to extract only the main article
            # and stop before related articles sections
            if selector == '.restrictedcontent':
                # Get all paragraphs in order
                all_paragraphs = content_elem.find_all('p', recursive=True)
                main_paragraphs = []
                
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    
                    # Skip very short paragraphs (likely metadata or separators)
                    if len(text) < 20:
                        continue
                    
                    # Check if this paragraph is part of a related articles section
                    # Look for parent elements that contain multiple article links
                    parent = p.find_parent(['div', 'section', 'ul', 'article'])
                    if parent:
                        # Count article links in the parent's siblings and the parent itself
                        article_links = parent.select('a[href$=".article"]')
                        
                        # If parent has 2+ article links and we already have substantial content, stop
                        if len(article_links) >= 2 and len(main_paragraphs) >= 3:
                            # Check if this looks like a list of articles (short lines with dates)
                            sibling_texts = [s.get_text(strip=True) for s in parent.find_all(['p', 'li', 'div'])[:5]]
                            date_patterns = sum(1 for t in sibling_texts if '2025-' in t or '2024-' in t)
                            
                            if date_patterns >= 2:  # Multiple date patterns = likely article list
                                break
                    
                    # Check for "Load more" or similar indicators
                    if any(keyword in text.lower() for keyword in ['load more', 'related articles', 'more news', 'see also']):
                        break
                    
                    # Add paragraph if it's substantial
                    if len(text) > 30:
                        main_paragraphs.append(text)
                
                if main_paragraphs and len('\n\n'.join(main_paragraphs)) > 200:
                    return '\n\n'.join(main_paragraphs)
            
            # For other selectors, use standard extraction
            # Remove script, style, nav, aside, footer, header elements
            for tag in content_elem(["script", "style", "nav", "aside", "footer", "header"]):
                tag.decompose()
            
            # Remove the title if it's in the main content
            h1_in_content = content_elem.select_one('h1')
            if h1_in_content:
                h1_in_content.decompose()
            
            # Remove navigation, breadcrumbs, and other non-content elements
            for tag in content_elem.select('.nav, .navigation, .breadcrumb, .social-share, .tags, .author, .pagination, .related-articles, .more-news'):
                tag.decompose()
            
            # Remove sections with multiple article links (related articles)
            for elem in content_elem.find_all(['div', 'section', 'ul']):
                article_links = elem.select('a[href$=".article"]')
                if len(article_links) >= 3:  # 3+ article links = related articles section
                    elem.decompose()
            
            # Get text and clean it up
            text = content_elem.get_text(separator='\n', strip=True)
            
            # Validate: if text contains too many "News" keywords, it might be a listing
            news_count = text.lower().count('news')
            if news_count > 15 and len(text) < 5000:  # Suspicious pattern
                continue  # Try next selector
            
            if len(text) > 200:  # Reasonable content length
                return text
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup, url: str) -> Optional[datetime]:
        """Extract published date."""
        from dateutil import parser as date_parser
        
        # Try multiple date selectors
        selectors = [
            'time[datetime]',
            'time',
            '.date',
            '.published-date',
            '.article-date',
            '[class*="date"]',
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
        
        # Fallback: try to extract from URL
        # aircargonews.net URLs sometimes have dates
        import re
        date_pattern = r'/(\d{4})/(\d{2})/(\d{2})/'
        match = re.search(date_pattern, url)
        if match:
            try:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day))
            except:
                pass
        
        return None

