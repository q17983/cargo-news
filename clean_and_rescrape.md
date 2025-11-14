# Clean Supabase Data and Rescrape Guide

## Step 1: Clean Supabase Data

### Option A: Via Supabase Dashboard (Recommended)
1. Go to https://app.supabase.com
2. Select your project
3. Go to **Table Editor**
4. Delete data in this order:
   - `bookmarks` table → Delete all rows
   - `articles` table → Delete all rows
   - `scraping_logs` table → Delete all rows
   - `news_sources` table → Delete all rows (if you want to start fresh)

### Option B: Via SQL Editor
Run this SQL in Supabase SQL Editor:

```sql
-- Delete all data (in correct order due to foreign keys)
DELETE FROM bookmarks;
DELETE FROM articles;
DELETE FROM scraping_logs;
DELETE FROM news_sources;

-- Reset sequences (optional, for clean IDs)
ALTER SEQUENCE IF EXISTS news_sources_id_seq RESTART WITH 1;
```

## Step 2: Verify 20-Page Limit

The limit is already set to **20 pages** for first-time scraping in:
- ✅ `app/api/routes/scrape.py` (line 57)
- ✅ `scrape_stattimes.py` (line 134)
- ✅ `scrape_aircargonews.py` (line 134)
- ✅ `scrape_aircargoweek.py` (line 134)

## Step 3: Rescrape from 3 Sources

### Option A: Via Web UI (Recommended)
1. Start backend: `uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Go to http://localhost:3000/sources
4. Add the 3 sources:
   - https://www.stattimes.com/latest-news
   - https://www.aircargonews.net/latest-news/31.more?navcode=28&page=1
   - https://aircargoweek.com/news/
5. Click "Scrape" button for each source (one at a time)
6. Wait for each to complete before starting the next

### Option B: Via Standalone Scripts
Run each script separately (wait for each to finish):

```bash
# Source 1: STAT Times
python3 scrape_stattimes.py --max-pages 20

# Wait for completion, then:
# Source 2: Air Cargo News
python3 scrape_aircargonews.py --max-pages 20

# Wait for completion, then:
# Source 3: Air Cargo Week
python3 scrape_aircargoweek.py --max-pages 20
```

## Step 4: Monitor Progress

- Check Supabase `articles` table for new articles
- Check `scraping_logs` table for status
- Watch for quota errors (should be fine with 20 pages = ~200-400 articles per source)

## Important Notes

- **20 pages = ~200-400 articles per source**
- **Total: ~600-1,200 articles across 3 sources**
- **This is within free tier limits** (1,500 requests/day)
- **Scrape one source at a time** to avoid hitting quota
- **Wait 1-2 hours between sources** if you want to be extra safe

