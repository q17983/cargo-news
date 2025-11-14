"""Supabase client for database operations."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from supabase import create_client, Client
from app.config import settings
from app.database.models import (
    NewsSource, NewsSourceCreate, NewsSourceUpdate,
    Article, ArticleCreate, ArticleUpdate,
    ScrapingLog, ScrapingLogCreate
)

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase client initialized")
    
    # News Sources Operations
    
    def create_source(self, source: NewsSourceCreate) -> NewsSource:
        """Create a new news source."""
        try:
            data = source.model_dump(exclude_none=True, mode='json')
            response = self.client.table('news_sources').insert(data).execute()
            
            if response.data:
                return NewsSource(**response.data[0])
            raise Exception("No data returned from insert")
        except Exception as e:
            logger.error(f"Error creating source: {str(e)}")
            raise
    
    def get_source(self, source_id: UUID) -> Optional[NewsSource]:
        """Get a news source by ID."""
        try:
            response = self.client.table('news_sources').select('*').eq('id', str(source_id)).execute()
            if response.data:
                return NewsSource(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting source: {str(e)}")
            return None
    
    def get_all_sources(self, active_only: bool = False) -> List[NewsSource]:
        """Get all news sources."""
        try:
            query = self.client.table('news_sources').select('*')
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.execute()
            return [NewsSource(**item) for item in response.data]
        except Exception as e:
            logger.error(f"Error getting sources: {str(e)}")
            return []
    
    def update_source(self, source_id: UUID, update: NewsSourceUpdate) -> Optional[NewsSource]:
        """Update a news source."""
        try:
            data = update.model_dump(exclude_none=True)
            response = self.client.table('news_sources').update(data).eq('id', str(source_id)).execute()
            
            if response.data:
                return NewsSource(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating source: {str(e)}")
            return None
    
    def delete_source(self, source_id: UUID) -> bool:
        """Delete a news source."""
        try:
            self.client.table('news_sources').delete().eq('id', str(source_id)).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting source: {str(e)}")
            return False
    
    # Articles Operations
    
    def article_exists(self, url: str, title: Optional[str] = None) -> bool:
        """
        Check if an article already exists by URL or title.
        
        Args:
            url: Article URL (primary check)
            title: Article title (secondary check if URL check fails)
            
        Returns:
            True if article exists, False otherwise
        """
        try:
            # Primary check: by URL (most reliable)
            response = self.client.table('articles').select('id').eq('url', url).limit(1).execute()
            if len(response.data) > 0:
                return True
            
            # Secondary check: by title (in case URL changed but same article)
            # Only check recent articles to avoid performance issues
            if title and len(title) > 10:
                # Normalize title for comparison
                normalized_title = ' '.join(title.lower().split())
                # Get first few words as a search key
                title_words = normalized_title.split()[:5]  # First 5 words
                if len(title_words) >= 3:
                    search_key = ' '.join(title_words)
                    # Query articles with similar title words (limit to recent 100 for performance)
                    response = self.client.table('articles').select('id, title').limit(100).order('created_at', desc=True).execute()
                    for article in response.data:
                        if article.get('title'):
                            existing_title = ' '.join(article['title'].lower().split())
                            # Check if titles are very similar (90% match)
                            if self._titles_similar(normalized_title, existing_title):
                                logger.info(f"Article with similar title already exists: {existing_title[:50]}...")
                                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking article existence: {str(e)}")
            return False
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.9) -> bool:
        """Check if two titles are similar (to detect duplicates with slight variations)."""
        if not title1 or not title2:
            return False
        
        # Simple similarity check: if one title contains most of the other
        shorter = min(len(title1), len(title2))
        longer = max(len(title1), len(title2))
        
        if shorter == 0:
            return False
        
        # Count common words
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return False
        
        common_words = words1.intersection(words2)
        similarity = len(common_words) / max(len(words1), len(words2))
        
        return similarity >= threshold
    
    def create_article(self, article: ArticleCreate) -> Article:
        """Create a new article."""
        try:
            data = article.model_dump(exclude_none=True, mode='json')
            # Convert UUID to string for JSON serialization
            if 'source_id' in data and isinstance(data['source_id'], UUID):
                data['source_id'] = str(data['source_id'])
            response = self.client.table('articles').insert(data).execute()
            
            if response.data:
                return Article(**response.data[0])
            raise Exception("No data returned from insert")
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            raise
    
    def get_article(self, article_id: UUID) -> Optional[Article]:
        """Get an article by ID."""
        try:
            response = self.client.table('articles').select('*').eq('id', str(article_id)).execute()
            if response.data:
                return Article(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting article: {str(e)}")
            return None
    
    def get_articles_by_source(self, source_id: UUID, limit: int = 1) -> List[Article]:
        """Get articles for a specific source (for checking if source has been scraped before)."""
        try:
            query = self.client.table('articles').select('*').eq('source_id', str(source_id))
            query = query.order('created_at', desc=True).limit(limit)
            response = query.execute()
            return [Article(**item) for item in response.data]
        except Exception as e:
            logger.error(f"Error getting articles by source: {str(e)}")
            return []
    
    def get_articles(
        self,
        source_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Article]:
        """Get articles with filtering."""
        try:
            query = self.client.table('articles').select('*')
            
            if source_id:
                query = query.eq('source_id', str(source_id))
            
            if date_from:
                query = query.gte('published_date', date_from.isoformat())
            
            if date_to:
                query = query.lte('published_date', date_to.isoformat())
            
            # Order by published_date descending (newest first), fallback to created_at
            # Note: PostgreSQL NULLS LAST ensures articles with dates come first
            query = query.order('published_date', desc=True)
            query = query.order('created_at', desc=True)
            
            # Apply limit and offset
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            articles = [Article(**item) for item in response.data]
            
            # Filter by tags if provided (PostgreSQL array contains)
            if tags:
                filtered_articles = []
                for article in articles:
                    if any(tag in article.tags for tag in tags):
                        filtered_articles.append(article)
                articles = filtered_articles
            
            return articles
        except Exception as e:
            logger.error(f"Error getting articles: {str(e)}")
            return []
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags from articles."""
        try:
            response = self.client.table('articles').select('tags').execute()
            tags_set = set()
            for item in response.data:
                if item.get('tags'):
                    tags_set.update(item['tags'])
            return sorted(list(tags_set))
        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            return []
    
    def update_article(self, article_id: UUID, update: ArticleUpdate) -> Optional[Article]:
        """Update an article."""
        try:
            data = update.model_dump(exclude_none=True)
            response = self.client.table('articles').update(data).eq('id', str(article_id)).execute()
            
            if response.data:
                return Article(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating article: {str(e)}")
            return None
    
    # Scraping Logs Operations
    
    def create_scraping_log(self, log: ScrapingLogCreate) -> ScrapingLog:
        """Create a scraping log entry."""
        try:
            data = log.model_dump(exclude_none=True, mode='json')
            # Convert UUID to string for JSON serialization
            if 'source_id' in data and isinstance(data['source_id'], UUID):
                data['source_id'] = str(data['source_id'])
            response = self.client.table('scraping_logs').insert(data).execute()
            
            if response.data:
                return ScrapingLog(**response.data[0])
            raise Exception("No data returned from insert")
        except Exception as e:
            logger.error(f"Error creating scraping log: {str(e)}")
            raise
    
    def get_scraping_logs(self, source_id: Optional[UUID] = None, limit: int = 50) -> List[ScrapingLog]:
        """Get scraping logs."""
        try:
            query = self.client.table('scraping_logs').select('*')
            
            if source_id:
                query = query.eq('source_id', str(source_id))
            
            query = query.order('created_at', desc=True).limit(limit)
            
            response = query.execute()
            return [ScrapingLog(**item) for item in response.data]
        except Exception as e:
            logger.error(f"Error getting scraping logs: {str(e)}")
            return []
    
    def create_bookmark(self, article_id: UUID) -> None:
        """Create a bookmark for an article."""
        try:
            self.client.table('bookmarks').insert({
                'article_id': str(article_id)
            }).execute()
        except Exception as e:
            logger.error(f"Error creating bookmark: {str(e)}")
            raise
    
    def delete_bookmark(self, article_id: UUID) -> None:
        """Delete a bookmark for an article."""
        try:
            self.client.table('bookmarks').delete().eq('article_id', str(article_id)).execute()
        except Exception as e:
            logger.error(f"Error deleting bookmark: {str(e)}")
            raise
    
    def is_bookmarked(self, article_id: UUID) -> bool:
        """Check if an article is bookmarked."""
        try:
            response = self.client.table('bookmarks').select('id').eq('article_id', str(article_id)).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking bookmark: {str(e)}")
            return False
    
    def get_bookmarks(self) -> List[Dict[str, Any]]:
        """Get all bookmarked articles with article details."""
        try:
            # Join bookmarks with articles
            response = self.client.table('bookmarks').select(
                'id, created_at, article:articles(*)'
            ).order('created_at', desc=True).execute()
            
            bookmarks = []
            for item in response.data:
                if item.get('article'):
                    article = item['article']
                    # Enrich with source information
                    source = self.get_source(UUID(article['source_id']))
                    if source:
                        from urllib.parse import urlparse
                        parsed = urlparse(source.url)
                        article['source'] = {
                            'id': str(source.id),
                            'name': source.name or parsed.netloc.replace('www.', ''),
                            'url': source.url,
                            'domain': parsed.netloc.replace('www.', '')
                        }
                    bookmarks.append({
                        'id': item['id'],
                        'created_at': item['created_at'],
                        'article': article
                    })
            
            return bookmarks
        except Exception as e:
            logger.error(f"Error getting bookmarks: {str(e)}")
            return []


# Global instance
db = SupabaseClient()

