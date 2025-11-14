# Cargo News Aggregator System

A full-stack application that scrapes air cargo news websites, summarizes articles using Google Gemini API in Traditional Chinese, stores them in Supabase, and provides a web UI for source registration and article filtering by tags.

## Features

- Automated daily scraping of air cargo news websites at 00:00 UTC
- AI-powered summarization in Traditional Chinese using Google Gemini API
- Intelligent tagging system for article categorization
- Web UI for source management and article filtering
- Supabase database for reliable data storage

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React/Next.js
- **Database**: Supabase (PostgreSQL)
- **Scraping**: BeautifulSoup4, requests, Selenium/Playwright
- **AI**: Google Gemini API
- **Scheduling**: APScheduler
- **Deployment**: Railway

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials
5. Set up Supabase database (see database schema in docs)
6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

See `.env.example` for required environment variables.

## Database Schema

The application requires three main tables in Supabase:
- `news_sources`: Stores registered news sources
- `articles`: Stores scraped articles with summaries and tags
- `scraping_logs`: Tracks scraping activities

## Deployment

The application is configured for Railway deployment. See `railway.json` for configuration.

## License

MIT

