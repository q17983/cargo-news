"""API routes for bookmarks."""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.database.supabase_client import db
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class BookmarkCreate(BaseModel):
    """Model for creating a bookmark."""
    article_id: UUID


@router.post("")
async def create_bookmark(bookmark: BookmarkCreate):
    """Create a bookmark for an article."""
    try:
        db.create_bookmark(bookmark.article_id)
        return {"message": "Bookmark created", "article_id": str(bookmark.article_id)}
    except Exception as e:
        logger.error(f"Error creating bookmark: {str(e)}")
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Article is already bookmarked"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bookmark: {str(e)}"
        )


@router.delete("/{article_id}")
async def delete_bookmark(article_id: UUID):
    """Delete a bookmark for an article."""
    try:
        db.delete_bookmark(article_id)
        return {"message": "Bookmark deleted", "article_id": str(article_id)}
    except Exception as e:
        logger.error(f"Error deleting bookmark: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting bookmark: {str(e)}"
        )


@router.get("/{article_id}")
async def check_bookmark(article_id: UUID):
    """Check if an article is bookmarked."""
    try:
        is_bookmarked = db.is_bookmarked(article_id)
        return {"is_bookmarked": is_bookmarked, "article_id": str(article_id)}
    except Exception as e:
        logger.error(f"Error checking bookmark: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking bookmark: {str(e)}"
        )


@router.get("")
async def get_bookmarks():
    """Get all bookmarked articles."""
    try:
        bookmarks = db.get_bookmarks()
        return bookmarks
    except Exception as e:
        logger.error(f"Error getting bookmarks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving bookmarks: {str(e)}"
        )

