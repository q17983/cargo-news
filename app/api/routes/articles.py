"""API routes for articles."""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from uuid import UUID
from datetime import datetime
from app.database.supabase_client import db
from app.database.models import Article

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_articles(
    source_id: Optional[UUID] = Query(None, description="Filter by source ID"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    date_from: Optional[datetime] = Query(None, description="Filter articles from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter articles until this date"),
    limit: int = Query(1000, ge=1, le=2000, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip")
):
    """Get articles with optional filtering. Includes source information."""
    try:
        articles = db.get_articles(
            source_id=source_id,
            tags=tags,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        # Enrich articles with source information
        enriched_articles = []
        sources_cache = {}
        
        for article in articles:
            article_dict = article.model_dump(mode='json')
            
            # Get source information
            if article.source_id not in sources_cache:
                source = db.get_source(article.source_id)
                if source:
                    from urllib.parse import urlparse
                    parsed = urlparse(source.url)
                    sources_cache[article.source_id] = {
                        'id': str(source.id),
                        'name': source.name or parsed.netloc.replace('www.', ''),
                        'url': source.url,
                        'domain': parsed.netloc.replace('www.', '')
                    }
                else:
                    sources_cache[article.source_id] = {
                        'id': str(article.source_id),
                        'name': 'Unknown Source',
                        'url': '',
                        'domain': ''
                    }
            
            article_dict['source'] = sources_cache[article.source_id]
            enriched_articles.append(article_dict)
        
        return enriched_articles
    except Exception as e:
        logger.error(f"Error getting articles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving articles: {str(e)}"
        )


@router.get("/{article_id}")
async def get_article(article_id: UUID):
    """Get a specific article by ID. Includes source information."""
    article = db.get_article(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Enrich with source information
    article_dict = article.model_dump(mode='json')
    source = db.get_source(article.source_id)
    if source:
        from urllib.parse import urlparse
        parsed = urlparse(source.url)
        article_dict['source'] = {
            'id': str(source.id),
            'name': source.name or parsed.netloc.replace('www.', ''),
            'url': source.url,
            'domain': parsed.netloc.replace('www.', '')
        }
    else:
        article_dict['source'] = {
            'id': str(article.source_id),
            'name': 'Unknown Source',
            'url': '',
            'domain': ''
        }
    
    return article_dict


@router.get("/tags/list", response_model=List[str])
async def get_tags():
    """Get all unique tags from articles."""
    try:
        tags = db.get_all_tags()
        return tags
    except Exception as e:
        logger.error(f"Error getting tags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tags: {str(e)}"
        )

