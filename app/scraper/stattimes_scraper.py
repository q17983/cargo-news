"""STAT Times (stattimes.com) specific scraper."""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from urllib.parse import urljoin, urlparse
from app.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class StattimesScraper(BaseScraper):
    """Scraper for stattimes.com."""
    
    BASE_URL = "https://www.stattimes.com"
    
    def __init__(self, delay_seconds: int = 2, max_retries: int = 3):
        """Initialize the stattimes.com scraper."""
        super().__init__(delay_seconds, max_retries)
    
    def get_article_urls(self, listing_url: str, max_pages: int = 5, check_duplicates: bool = False, duplicate_check_func = None) -> List[str]:
        """
        Extract article URLs from listing pages.
        STAT Times uses pagination like: /latest-news, /latest-news/2, /latest-news/3, etc.
        Uses Playwright for better handling of dynamic content.
        
        Args:
            listing_url: URL of the listing page (e.g., https://www.stattimes.com/latest-news)
            max_pages: Maximum number of pages to scrape
            check_duplicates: If True, check for duplicates and stop early when finding too many
            duplicate_check_func: Function to check if URL exists (url) -> bool
            
        Returns:
            List of article URLs
        """
        article_urls = []
        consecutive_duplicate_pages = 0
        max_consecutive_duplicates = 2  # Stop after 2 pages of all duplicates
        
        # Extract base URL and ensure it's the listing page
        parsed = urlparse(listing_url)
        base_path = parsed.path.rstrip('/')
        if not base_path.endswith('latest-news'):
            # If not already on latest-news, construct it
            base_path = '/latest-news'
        
        base_listing_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
        
        # Use base fetch_page method which already has Playwright fallback
        # This is more reliable than using Playwright directly
        for page_num in range(1, max_pages + 1):
            # Construct page URL: /latest-news for page 1, /latest-news/2 for page 2, etc.
            if page_num == 1:
                page_url = base_listing_url
            else:
                page_url = f"{base_listing_url}/{page_num}"
            
            logger.info(f"Scraping page {page_num}: {page_url}")
            
            soup = self.fetch_page(page_url)
            if not soup:
                logger.warning(f"Failed to fetch page {page_num}")
                break
            
            # Extract article URLs from current page
            page_urls = self._extract_article_urls_from_page(soup, page_url)
            
            if not page_urls:
                logger.warning(f"No articles found on page {page_num}, stopping")
                break
            
            # Check for duplicates if enabled
            if check_duplicates and duplicate_check_func:
                new_urls = []
                duplicate_count = 0
                
                for url in page_urls:
                    if duplicate_check_func(url):
                        duplicate_count += 1
                    else:
                        new_urls.append(url)
                
                logger.info(f"Page {page_num}: Found {len(page_urls)} URLs, {duplicate_count} duplicates, {len(new_urls)} new")
                
                if len(new_urls) == 0:
                    consecutive_duplicate_pages += 1
                    logger.info(f"All articles on page {page_num} are duplicates ({consecutive_duplicate_pages}/{max_consecutive_duplicates})")
                    if consecutive_duplicate_pages >= max_consecutive_duplicates:
                        logger.info(f"Stopping early: Found {max_consecutive_duplicates} consecutive pages with all duplicates")
                        break
                else:
                    consecutive_duplicate_pages = 0
                    article_urls.extend(new_urls)
            else:
                article_urls.extend(page_urls)
            
            # Check if there's a next page
            has_next_page = self._has_next_page(soup)
            if not has_next_page and page_num < max_pages:
                logger.info(f"No next page found after page {page_num}, stopping")
                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in article_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Total unique articles found: {len(unique_urls)}")
        return unique_urls
    
    def _extract_article_urls_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article URLs from a listing page."""
        urls = []
        seen = set()
        
        # STAT Times article links are typically in headings (h2, h3) or article containers
        # Look for links that match the article URL pattern: /{category}/{title-slug}-{numeric-id}
        all_links = soup.select('a[href]')
        
        logger.debug(f"Found {len(all_links)} total links on page")
        
        # Debug: log some sample links to understand structure
        sample_links = [link.get('href') for link in all_links[:10] if link.get('href')]
        logger.debug(f"Sample links: {sample_links[:5]}")
        
        for link in all_links:
            href = link.get('href')
            if not href:
                continue
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            
            # Filter for article URLs:
            # - Must be on stattimes.com domain
            # - Must have path like /{category}/{title-slug}-{numeric-id}
            # - Must not be the listing page itself
            if 'stattimes.com' not in parsed.netloc:
                continue
            
            # Skip if it's the listing page or pagination
            # Don't skip if it's an article URL that happens to contain "latest-news" in query params
            if '/latest-news' in parsed.path:
                # Only skip if it's exactly /latest-news or /latest-news/{number} (pagination)
                if parsed.path == '/latest-news' or re.match(r'^/latest-news/\d+/?$', parsed.path):
                    continue  # Skip listing/pagination pages
            
            path_parts = [p for p in parsed.path.split('/') if p]
            
            # Article URLs have pattern: /{category}/{title-slug}-{numeric-id}
            # Example: /air-cargo/hellmann-worldwide-logistics-partners-with-cargoone-to-boost-air-cargo-sales-1357045
            if len(path_parts) >= 2:
                # Check if last part ends with numeric ID (e.g., -1357045)
                last_part = path_parts[-1]
                if re.search(r'-\d+$', last_part):  # Ends with -{numbers}
                    # Additional validation: make sure it's not a category page
                    # Category pages usually don't have the numeric ID pattern
                    if absolute_url not in seen:
                        urls.append(absolute_url)
                        seen.add(absolute_url)
                        logger.debug(f"Found article URL: {absolute_url}")
        
        logger.info(f"Extracted {len(urls)} article URLs from page")
        return urls
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there's a next page available."""
        # Look for "Next Page >" link or similar pagination indicators
        # Check for pagination links
        pagination_links = soup.select('a[href*="/latest-news/"]')
        for link in pagination_links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # Check if it's a "next" link
            if 'next' in text or '>' in text:
                return True
        
        # Also check for any link with "Next Page" text
        all_links = soup.select('a')
        for link in all_links:
            text = link.get_text(strip=True).lower()
            if 'next' in text and 'page' in text:
                return True
        
        # Check if there are numbered page links (indicates pagination exists)
        # This is handled in get_article_urls by incrementing page_num
        # If we found pagination links, assume there might be more pages
        if pagination_links:
            return True
        
        return False
    
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
        # Try multiple selectors for STAT Times
        selectors = [
            'h1',
            '.article-title',
            '.post-title',
            'article h1',
            'main h1',
            '.entry-title',
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
        # STAT Times uses <article> tag for main content
        # Try article first, then fallback to other selectors
        selectors = [
            'article.entry-wraper',  # STAT Times specific class
            'article[class*="entry-wraper"]',  # More flexible match
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            'main article',
        ]
        
        for selector in selectors:
            content_elem = soup.select_one(selector)
            if not content_elem:
                logger.debug(f"Selector '{selector}' not found, trying next...")
                continue
            
            logger.debug(f"Found content element with selector '{selector}'")
            
            # Remove unwanted elements first
            for tag in content_elem(["script", "style", "nav", "aside", "footer", "header"]):
                tag.decompose()
            
            # Remove breadcrumbs (Home / Air Cargo / ...)
            for breadcrumb in content_elem.select('.breadcrumb, .breadcrumbs, [class*="breadcrumb"], nav[aria-label*="breadcrumb"]'):
                breadcrumb.decompose()
            
            # Remove the title (h1)
            h1_in_content = content_elem.select_one('h1')
            if h1_in_content:
                h1_in_content.decompose()
            
            # Remove author/byline/meta sections
            for elem in content_elem.select('.author, .byline, .post-meta, .article-meta, [class*="meta"], [class*="author"]'):
                elem.decompose()
            
            # Remove social share buttons
            for elem in content_elem.select('.social-share, [class*="share"], [class*="social"]'):
                elem.decompose()
            
            # Remove "Next Story", "Related Posts" sections
            for elem in content_elem.find_all(['div', 'section', 'aside']):
                text = elem.get_text(strip=True).lower()
                if any(keyword in text for keyword in ['next story', 'related posts', 'related articles', 'you may also like']):
                    elem.decompose()
            
            # Remove elements with multiple article links (likely related articles)
            # But be careful not to remove the main article content
            # Only remove if it's clearly a separate section (sidebar, footer, etc.)
            for elem in content_elem.find_all(['div', 'section', 'ul', 'aside']):
                article_links = elem.select('a[href*="stattimes.com/"]')
                # Only remove if it has many article links (5+) AND is not the main content
                # Check if this element contains most of the article paragraphs
                paragraphs_in_elem = elem.select('p')
                total_paragraphs = len(content_elem.select('p'))
                
                # If this element contains most paragraphs, it's likely the main content - don't remove
                if total_paragraphs > 0 and len(paragraphs_in_elem) > total_paragraphs * 0.5:
                    continue  # This is likely the main content, not a related articles section
                
                # Only remove if it has many article links (5+) and is clearly a separate section
                if len(article_links) >= 5:
                    # Additional check: make sure it's not the main article wrapper
                    elem_classes = elem.get('class', [])
                    if 'entry-wraper' in elem_classes or 'article' in ' '.join(elem_classes).lower():
                        continue  # Don't remove the main article wrapper
                    elem.decompose()
            
            # Extract paragraphs - the actual article content
            paragraphs = content_elem.select('p')
            content_paragraphs = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Skip very short paragraphs
                if len(text) < 30:
                    continue
                
                # Skip paragraphs that are clearly breadcrumbs/navigation
                # Breadcrumbs typically have: "Home / Latest News / Article Title" pattern
                text_lower = text.lower()
                
                # Check for breadcrumb pattern: starts with "Home" and has multiple slashes
                if text_lower.startswith('home') and text.count('/') >= 2:
                    continue
                
                # Skip if it's clearly navigation (short text with multiple slashes)
                if text.count('/') >= 3 and len(text) < 100:
                    continue
                
                # Skip metadata lines
                if any(keyword in text_lower for keyword in ['by stat times', 'loading...', 'next story', 'related posts', 'one stop destination']):
                    continue
                
                # Skip promotional/ad text
                if 'one stop destination' in text_lower or 'your logistics' in text_lower:
                    continue
                
                # This looks like valid article content
                content_paragraphs.append(text)
            
            # If we found good paragraphs, use them
            logger.debug(f"Found {len(content_paragraphs)} valid paragraphs from selector '{selector}'")
            if len(content_paragraphs) >= 2:  # Reduced from 3 to 2 for shorter articles
                content = '\n\n'.join(content_paragraphs)
                # Clean up excessive whitespace
                content = re.sub(r'\n{3,}', '\n\n', content)
                logger.debug(f"Content length: {len(content)} chars")
                if len(content) > 200:  # Reasonable content length
                    logger.debug(f"Returning content from selector '{selector}'")
                    return content
                else:
                    logger.debug(f"Content too short ({len(content)} chars), trying next selector...")
            else:
                logger.debug(f"Not enough paragraphs ({len(content_paragraphs)}), trying next selector...")
            
            # Fallback: get all text if paragraph extraction didn't work well
            text = content_elem.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # Remove breadcrumb-like lines (contain multiple slashes)
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip lines that look like breadcrumbs
                # Pattern: "Home / Latest News / Article Title" or similar
                line_lower = line.lower()
                if line_lower.startswith('home') and line.count('/') >= 2:
                    continue
                
                # Skip navigation lines (multiple slashes in short text)
                if line.count('/') >= 3 and len(line) < 50:
                    continue
                
                # Skip metadata lines
                if any(keyword in line_lower for keyword in ['by stat times', 'loading...', 'next story', 'related posts', 'one stop destination']):
                    continue
                
                # Skip very short lines that are likely metadata
                if len(line) < 10:
                    continue
                
                cleaned_lines.append(line)
            
            cleaned_text = '\n\n'.join(cleaned_lines)
            
            # Final check: make sure we don't have breadcrumbs at the start
            if cleaned_text.startswith('Home') or 'Home /' in cleaned_text[:100]:
                # Try to find where actual content starts
                content_start = 0
                for i, line in enumerate(cleaned_lines):
                    if not (line.lower().startswith('home') and '/' in line):
                        content_start = i
                        break
                if content_start > 0:
                    cleaned_text = '\n\n'.join(cleaned_lines[content_start:])
            
            if len(cleaned_text) > 200:  # Reasonable content length
                return cleaned_text
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup, url: str) -> Optional[datetime]:
        """Extract published date."""
        # STAT Times date formats:
        # - "BySTAT Times|3 Apr 2025 9:55 PM"
        # - "6 Nov 2025 5:16 PM IST"
        # - "3 Apr 2025 9:55 PM"
        
        # First, try to find the "BySTAT Times|" pattern
        # This is often in the byline or article metadata
        page_text = soup.get_text()
        
        # Pattern 1: "BySTAT Times|3 Apr 2025 9:55 PM" or "By STAT Times|3 Apr 2025 9:55 PM"
        byline_pattern = r'By\s*STAT\s*Times\s*\|\s*(\d{1,2}\s+\w+\s+\d{4}\s+\d{1,2}:\d{2}\s+(?:AM|PM))'
        match = re.search(byline_pattern, page_text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                return date_parser.parse(date_str)
            except ValueError:
                pass
        
        # Pattern 2: "BySTAT Times|3 Apr 2025" (without time)
        byline_pattern_no_time = r'By\s*STAT\s*Times\s*\|\s*(\d{1,2}\s+\w+\s+\d{4})'
        match = re.search(byline_pattern_no_time, page_text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                return date_parser.parse(date_str)
            except ValueError:
                pass
        
        # Pattern 3: Look for date in byline/metadata sections
        # Check common byline/metadata selectors
        byline_selectors = [
            '.byline',
            '.article-byline',
            '.post-byline',
            '.author',
            '.article-meta',
            '.post-meta',
            '[class*="byline"]',
            '[class*="author"]',
        ]
        
        for selector in byline_selectors:
            byline_elems = soup.select(selector)
            for byline in byline_elems:
                text = byline.get_text()
                # Look for "BySTAT Times|" pattern
                match = re.search(r'By\s*STAT\s*Times\s*\|\s*(\d{1,2}\s+\w+\s+\d{4}(?:\s+\d{1,2}:\d{2}\s+(?:AM|PM))?)', text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    try:
                        return date_parser.parse(date_str)
                    except ValueError:
                        pass
        
        # Pattern 4: Try standard date selectors
        date_selectors = [
            'time[datetime]',
            'time',
            '.date',
            '.published-date',
            '.article-date',
            '.post-date',
            '.entry-date',
            '[class*="date"]',
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                # Try datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    try:
                        return date_parser.parse(datetime_attr)
                    except ValueError:
                        pass
                
                # Try text content
                date_text = date_elem.get_text(strip=True)
                if date_text:
                    try:
                        return date_parser.parse(date_text)
                    except ValueError:
                        pass
        
        # Pattern 5: Search entire page for date patterns like "3 Apr 2025 9:55 PM"
        # This is a more general pattern that should catch most STAT Times dates
        date_patterns = [
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s+\d{1,2}:\d{2}\s+(?:AM|PM))',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    return date_parser.parse(date_str)
                except ValueError:
                    pass
        
        # Fallback: try to extract from URL if date is embedded (less common)
        date_match = re.search(r'(\d{4}/\d{2}/\d{2})', url)
        if date_match:
            try:
                return datetime.strptime(date_match.group(1), '%Y/%m/%d')
            except ValueError:
                pass
        
        logger.warning(f"Could not extract date from article: {url}")
        return None

