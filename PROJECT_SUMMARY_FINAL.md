# 🚀 Cargo News Aggregator - Complete Project Summary

## 📋 What We've Built

A complete **Air Cargo News Aggregation System** that:

### ✅ Core Features
1. **Web Scraping** - Automatically scrapes articles from air cargo news websites
2. **AI Summarization** - Uses Google Gemini API to generate Traditional Chinese summaries
3. **Tag Extraction** - Automatically extracts tags (companies, topics, geography) from articles
4. **Database Storage** - Saves everything to Supabase (PostgreSQL)
5. **Web Interface** - Beautiful React/Next.js frontend to view and filter articles
6. **Duplicate Prevention** - Smart duplicate detection by URL and title
7. **Smart Pagination** - Scrapes more pages on first run, fewer on daily runs
8. **Background Processing** - Scraping runs in background without blocking the server

### 🎯 Supported News Sources

1. **Air Cargo News** (`aircargonews.net`)
   - Custom scraper: `AircargonewsScraper`
   - Listing URL: `/latest-news/31.more?navcode=28`
   - Status: ✅ Working

2. **Air Cargo Week** (`aircargoweek.com`)
   - Custom scraper: `AircargoweekScraper`
   - Listing URL: `/news/`
   - Uses Playwright for dynamic content
   - Status: ✅ Working

### 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  Next.js/React (port 3000)
│   (Web UI)      │  - View articles
└────────┬────────┘  - Filter by tags
         │           - Manage sources
         │
         │ HTTP API
         │
┌────────▼────────┐
│   Backend       │  FastAPI (port 8000)
│   (Python)      │  - API endpoints
└────────┬────────┘  - Background tasks
         │           - Daily scheduler
         │
         ├──────────┐
         │          │
┌────────▼────┐  ┌─▼────────────┐
│  Scrapers   │  │  AI          │
│             │  │  Summarizer  │
│ - Base      │  │  (Gemini)    │
│ - Aircargo  │  │              │
│   News      │  └──────────────┘
│ - Aircargo  │
│   Week      │
└──────┬──────┘
       │
┌──────▼──────┐
│  Supabase   │  PostgreSQL Database
│  (Database) │  - Articles
│             │  - Sources
│             │  - Scraping logs
└─────────────┘
```

### 📁 Project Structure

```
Cargo News/
├── app/                          # Backend (Python/FastAPI)
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration (env vars)
│   ├── api/
│   │   └── routes/
│   │       ├── sources.py       # Source management API
│   │       ├── articles.py      # Article retrieval API
│   │       └── scrape.py        # Scraping trigger API
│   ├── scraper/
│   │   ├── base_scraper.py      # Base scraper class
│   │   ├── aircargonews_scraper.py
│   │   ├── aircargoweek_scraper.py
│   │   └── scraper_factory.py   # Scraper selection
│   ├── ai/
│   │   └── summarizer.py        # Gemini AI integration
│   ├── database/
│   │   ├── models.py            # Pydantic models
│   │   └── supabase_client.py   # Database operations
│   └── scheduler/
│       └── daily_scraper.py     # Daily auto-scraping
│
├── frontend/                     # Frontend (Next.js/React)
│   ├── app/
│   │   ├── page.tsx             # Articles page
│   │   ├── sources/
│   │   │   └── page.tsx         # Sources management
│   │   └── articles/[id]/
│   │       └── page.tsx         # Article detail
│   └── components/
│       ├── ArticleList.tsx
│       ├── SourceList.tsx
│       └── TagFilter.tsx
│
├── scrape_aircargoweek.py       # Standalone scraping script
├── test_aircargoweek.py         # Testing script
├── requirements.txt              # Python dependencies
├── database_schema.sql           # Database schema
└── .env                          # Environment variables
```

### 🔧 Key Technologies

- **Backend**: Python 3.x, FastAPI, Uvicorn
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini API
- **Scraping**: BeautifulSoup4, Playwright, Requests
- **Scheduling**: APScheduler
- **Deployment**: Railway (ready)

### 🚀 How to Run

#### Option 1: Full System (Recommended for Production)

**Terminal 1 - Backend:**
```bash
cd "/Users/sai/Cargo News"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd "/Users/sai/Cargo News/frontend"
npm run dev
```

Then visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Option 2: Standalone Script (For Testing)

**Run scraping script directly:**
```bash
cd "/Users/sai/Cargo News"
source venv/bin/activate
python3 scrape_aircargoweek.py --max-pages 3
```

### 📝 Environment Variables (.env)

```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Google Gemini
GEMINI_API_KEY=AIzaSyCSg4pvORmJmdsfPLqmZ41Ia5v9kDNS1Dg

# Server
PORT=8000
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
```

### 🎯 Main Workflows

#### 1. Adding a News Source
- Go to `/sources` page
- Click "Add Source"
- Enter URL (e.g., `https://aircargoweek.com/news/`)
- System automatically selects the right scraper
- Optionally auto-scrape immediately

#### 2. Scraping Articles
**Via Web Interface:**
- Click "Scrape" button next to a source
- Runs in background
- Articles appear as they're processed

**Via Script:**
- Run `python3 scrape_aircargoweek.py`
- See real-time progress
- Articles saved to database

#### 3. Viewing Articles
- Go to homepage (`/`)
- Filter by tags
- Click article to read full summary
- All summaries in Traditional Chinese

#### 4. Daily Automation
- Built-in scheduler runs at 00:00 UTC daily
- Scrapes all active sources automatically
- Smart pagination (stops early on duplicates)

### 🔑 Key Files to Run

#### For Full System:
1. **`app/main.py`** - Backend server (via `uvicorn app.main:app`)
2. **`frontend/app/page.tsx`** - Frontend (via `npm run dev`)

#### For Standalone Scraping:
1. **`scrape_aircargoweek.py`** - Complete scraping workflow

### 📊 Database Tables

1. **`news_sources`** - Registered news sources
2. **`articles`** - Scraped articles with summaries
3. **`scraping_logs`** - Scraping history and statistics

### ✨ Special Features

- **Smart Duplicate Detection**: Checks by URL and title similarity
- **Smart Pagination**: 
  - First run: Up to 100 pages
  - Daily runs: 3 pages, stops early on duplicates
- **Anti-Bot Measures**: Playwright fallback for blocked sites
- **Background Processing**: Non-blocking scraping via thread pool
- **Tag Extraction**: Automatic tagging (companies, topics, geography)
- **Traditional Chinese**: All summaries in Traditional Chinese

### 🎓 What You Can Do Now

1. ✅ Add news sources via web interface
2. ✅ Scrape articles manually (button or script)
3. ✅ View articles with Traditional Chinese summaries
4. ✅ Filter articles by tags
5. ✅ Automatic daily scraping (00:00 UTC)
6. ✅ Test scrapers before adding sources
7. ✅ View scraping logs and statistics

### 🚨 Important Notes

- **Playwright**: Must be installed (`playwright install chromium`)
- **Environment**: Must have `.env` file with API keys
- **Database**: Must run `database_schema.sql` in Supabase
- **Backend**: Must be running for web scraping button to work
- **Frontend**: Connects to backend at `http://localhost:8000`

---

## 🎉 Project Status: **COMPLETE & WORKING**

All features implemented and tested! 🚀

