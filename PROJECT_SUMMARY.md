# Cargo News Aggregator - Project Summary

## Overview

A complete full-stack application for aggregating and summarizing air cargo news articles. The system automatically scrapes news websites, uses AI to generate Traditional Chinese summaries, and provides a web interface for managing sources and filtering articles by tags.

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Database**: Supabase (PostgreSQL)
- **Scraping**: BeautifulSoup4 with anti-bot measures
- **AI**: OpenAI API for summarization
- **Scheduling**: APScheduler for daily scraping at 00:00 UTC

### Frontend (Next.js/React)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks

## Key Features

1. **Automated Web Scraping**
   - Anti-bot measures (rotating user agents, rate limiting)
   - Site-specific scrapers (aircargonews.net)
   - Pagination support
   - Duplicate detection

2. **AI-Powered Summarization**
   - OpenAI API integration
   - Traditional Chinese output
   - Structured summaries with sub-headings
   - Automatic tagging system

3. **Database Management**
   - Supabase PostgreSQL
   - Three main tables: news_sources, articles, scraping_logs
   - Full-text search and tag filtering

4. **Web Interface**
   - Dashboard with article listing
   - Tag-based filtering
   - Source management (add/edit/delete/test)
   - Article detail view

5. **Automated Scheduling**
   - Daily scraping at 00:00 UTC
   - Background task processing
   - Error logging and retry logic

## Project Structure

```
cargo-news/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── scraper/                # Web scraping modules
│   │   ├── base_scraper.py
│   │   ├── aircargonews_scraper.py
│   │   └── scraper_factory.py
│   ├── ai/                     # AI summarization
│   │   └── summarizer.py
│   ├── database/               # Database operations
│   │   ├── models.py
│   │   └── supabase_client.py
│   ├── scheduler/               # Scheduling
│   │   └── daily_scraper.py
│   └── api/                     # API routes
│       └── routes/
│           ├── sources.py
│           ├── articles.py
│           └── scrape.py
├── frontend/                    # Next.js frontend
│   ├── app/
│   ├── components/
│   └── lib/
├── database_schema.sql          # Database schema
├── requirements.txt             # Python dependencies
└── railway.json                 # Railway deployment config
```

## API Endpoints

### Sources
- `GET /api/sources` - List all sources
- `POST /api/sources` - Create new source
- `PUT /api/sources/{id}` - Update source
- `DELETE /api/sources/{id}` - Delete source
- `POST /api/sources/{id}/test` - Test source scraping

### Articles
- `GET /api/articles` - List articles (with filtering)
- `GET /api/articles/{id}` - Get article details
- `GET /api/articles/tags/list` - Get all tags

### Scraping
- `POST /api/scrape/{source_id}` - Scrape specific source
- `POST /api/scrape/all` - Scrape all active sources

## Environment Variables

Required:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `OPENAI_API_KEY` - OpenAI API key

Optional:
- `SCRAPING_DELAY_SECONDS` - Delay between requests (default: 2)
- `MAX_RETRIES` - Maximum retry attempts (default: 3)
- `PORT` - Server port (default: 8000)

## Deployment

### Railway
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Local Development
1. Set up virtual environment
2. Install dependencies
3. Configure `.env` file
4. Run backend: `uvicorn app.main:app --reload`
5. Run frontend: `cd frontend && npm run dev`

## Database Schema

### news_sources
- id (UUID)
- url (TEXT, UNIQUE)
- name (TEXT)
- selector_config (JSONB)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

### articles
- id (UUID)
- source_id (UUID, FK)
- title (TEXT)
- url (TEXT, UNIQUE)
- content (TEXT)
- summary (TEXT)
- tags (TEXT[])
- published_date (TIMESTAMP)
- scraped_at (TIMESTAMP)
- created_at (TIMESTAMP)

### scraping_logs
- id (UUID)
- source_id (UUID, FK)
- status (TEXT: success/failed/partial)
- error_message (TEXT)
- articles_found (INTEGER)
- created_at (TIMESTAMP)

## Next Steps

1. **Set up Supabase**: Create project and run schema SQL
2. **Get API Keys**: Obtain OpenAI API key
3. **Deploy to Railway**: Follow deployment guide
4. **Add First Source**: Use web UI to add aircargonews.net
5. **Test Scraping**: Manually trigger scraping
6. **Monitor**: Check logs and verify daily scraping

## Customization

### Adding New Scrapers
1. Create new scraper class in `app/scraper/`
2. Inherit from `BaseScraper`
3. Implement site-specific logic
4. Register in `scraper_factory.py`

### Modifying AI Prompt
1. Edit prompt template in `app/ai/summarizer.py`
2. Adjust parsing logic if format changes
3. Test with sample articles

### Frontend Customization
1. Modify components in `frontend/components/`
2. Update styles in `frontend/app/globals.css`
3. Add new pages in `frontend/app/`

## Support

For issues or questions:
1. Check logs in Railway dashboard
2. Review error messages in API responses
3. Test individual components (scraper, AI, database)
4. Verify environment variables are set correctly

## License

MIT

