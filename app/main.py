"""Main FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import sources, articles, scrape, bookmarks
from app.scheduler.daily_scraper import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cargo News Aggregator API",
    description="API for scraping and aggregating air cargo news",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["scrape"])
app.include_router(bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Cargo News Aggregator API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/keepalive")
async def keepalive():
    """Keep-alive endpoint to prevent Railway from sleeping."""
    return {"status": "alive", "message": "Service is running"}


@app.on_event("startup")
async def startup_event():
    """Startup event - initialize scheduler."""
    logger.info("Starting up application...")
    try:
        start_scheduler()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    logger.info("Shutting down application...")
    try:
        stop_scheduler()
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")

