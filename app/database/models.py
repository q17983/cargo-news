"""Pydantic models for database entities."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NewsSourceBase(BaseModel):
    """Base model for news source."""
    url: str
    name: Optional[str] = None
    selector_config: Optional[dict] = None
    is_active: bool = True


class NewsSourceCreate(NewsSourceBase):
    """Model for creating a news source."""
    pass


class NewsSourceUpdate(BaseModel):
    """Model for updating a news source."""
    url: Optional[str] = None
    name: Optional[str] = None
    selector_config: Optional[dict] = None
    is_active: Optional[bool] = None


class NewsSource(NewsSourceBase):
    """Model for news source response."""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    """Base model for article."""
    source_id: UUID
    title: str
    url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    published_date: Optional[datetime] = None


class ArticleCreate(ArticleBase):
    """Model for creating an article."""
    pass


class ArticleUpdate(BaseModel):
    """Model for updating an article."""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    published_date: Optional[datetime] = None


class Article(ArticleBase):
    """Model for article response."""
    id: UUID
    scraped_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScrapingLogBase(BaseModel):
    """Base model for scraping log."""
    source_id: UUID
    status: str  # 'success', 'failed', 'partial'
    error_message: Optional[str] = None
    articles_found: int = 0


class ScrapingLogCreate(ScrapingLogBase):
    """Model for creating a scraping log."""
    pass


class ScrapingLog(ScrapingLogBase):
    """Model for scraping log response."""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

