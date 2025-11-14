# How the "Scrape" Button Works - Complete Guide

## 🔍 Which Script Does the Button Call?

**The "Scrape" button does NOT call the standalone scripts** (`scrape_aircargonews.py` or `scrape_aircargoweek.py`).

Instead, it calls:
```
Frontend Button → API Endpoint → Backend Function
```

**Flow:**
1. **Frontend** (`frontend/lib/api.ts`): `triggerScrape(sourceId)`
2. **API Route** (`app/api/routes/scrape.py`): `POST /api/scrape/{source_id}`
3. **Function** (`app/api/routes/scrape.py`): `scrape_source(source_id)`
4. **Scraper** (`app/scraper/scraper_factory.py`): Automatically selects the right scraper
5. **Same code** as standalone scripts, but through the API

## 📊 How to See Progress

### Option 1: Check in Web Interface (NEW!)
The Sources page now shows:
- ✅ Last scraping status (success/failed/partial)
- ✅ Number of articles found
- ✅ When it last ran
- ✅ Auto-refreshes every 10 seconds

**Location:** Go to `/sources` page, look in the "Scraper" column

### Option 2: Check Scraping Logs via API
```bash
# Get latest status
curl http://localhost:8000/api/scrape/status/{source_id}

# Get recent logs
curl http://localhost:8000/api/scrape/logs/{source_id}?limit=10
```

### Option 3: Check Supabase Database
1. Go to Supabase dashboard
2. Open `scraping_logs` table
3. Filter by `source_id`
4. Check latest entry:
   - `status`: "success", "failed", or "partial"
   - `articles_found`: Total URLs found
   - `created_at`: When it finished

### Option 4: Check Articles Table
1. Go to Supabase dashboard
2. Open `articles` table
3. Filter by `source_id`
4. Sort by `created_at` DESC
5. New articles appear as they're processed

## 🛑 How to Stop Scraping

**⚠️ Important:** FastAPI BackgroundTasks **cannot be easily stopped** once started.

### Option 1: Restart Backend Server (Recommended)
```bash
# In terminal where uvicorn is running:
Ctrl+C  # Stop server

# Then restart:
uvicorn app.main:app --reload
```

This stops all background tasks.

### Option 2: Wait for Completion
- Scraping will finish on its own
- Usually takes 5-30 minutes depending on number of articles
- Check status to see when it's done

### Option 3: Kill Process (Not Recommended)
```bash
# Find process
ps aux | grep uvicorn

# Kill it
kill <PID>
```

## 📈 Progress Tracking

### What You Can See:
- ✅ **Status**: success, failed, partial, or never_scraped
- ✅ **Articles Found**: Total URLs discovered
- ✅ **Last Run Time**: When scraping completed
- ✅ **Error Messages**: If something went wrong

### What You CAN'T See (Currently):
- ❌ Real-time progress (how many articles processed so far)
- ❌ Estimated time remaining
- ❌ Current article being processed
- ❌ Live article count updates

### Why?
Background tasks run asynchronously. The web page returns immediately, and scraping happens in the background. There's no built-in way to stream progress updates to the frontend.

## 🔄 Comparison: Button vs Script

| Feature | Web Button | Standalone Script |
|---------|-----------|-------------------|
| **Code Called** | `app/api/routes/scrape.py` → `scrape_source()` | `scrape_aircargonews.py` → `_scrape_source_sync()` |
| **Execution** | Background (async) | Foreground (sync) |
| **Progress** | Check logs/status | Real-time in terminal |
| **Stop** | Restart server | Ctrl+C |
| **Best For** | Production use | Testing/debugging |

## 💡 Recommendations

### For Daily Use:
- ✅ Use the **web button**
- ✅ Check status in Sources page (auto-refreshes)
- ✅ Articles appear automatically when done
- ✅ No need to monitor constantly

### For Testing/Debugging:
- ✅ Use **standalone scripts** (`scrape_aircargonews.py` or `scrape_aircargoweek.py`)
- ✅ See real-time progress
- ✅ Can stop with Ctrl+C
- ✅ Better for troubleshooting

## 🎯 Quick Reference

**Check if scraping is done:**
```bash
# Via API
curl http://localhost:8000/api/scrape/status/{source_id}

# Or check Supabase scraping_logs table
```

**View scraping history:**
```bash
# Via API
curl http://localhost:8000/api/scrape/logs/{source_id}

# Or check Supabase scraping_logs table
```

**Stop scraping:**
- Restart backend server (Ctrl+C, then restart uvicorn)

**See new articles:**
- Go to homepage (`/`) - articles appear as they're processed
- Or check Supabase `articles` table

---

## Summary

**The "Scrape" button:**
- ✅ Calls `app/api/routes/scrape.py` → `scrape_source()` function
- ✅ Uses same scraping code as standalone scripts
- ✅ Runs in background (non-blocking)
- ✅ Shows status in Sources page (auto-refreshes)
- ❌ Can't see real-time progress
- ❌ Can't stop easily (restart server if needed)

**For real-time progress:** Use standalone scripts instead!

