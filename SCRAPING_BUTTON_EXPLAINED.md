# How the "Scrape" Button Works

## 🔄 Flow Diagram

```
User clicks "Scrape" button
    ↓
Frontend: POST /api/scrape/{source_id}
    ↓
Backend: app/api/routes/scrape.py → trigger_scrape()
    ↓
Backend: background_tasks.add_task(scrape_source, source_id)
    ↓
Returns immediately: {"message": "Scraping started..."}
    ↓
[Background Thread] _scrape_source_sync() runs:
    - Scrapes articles
    - Generates AI summaries
    - Saves to Supabase
    - Creates scraping log
    ↓
Articles appear in web interface
```

## 📝 Which Code is Called?

**When you click "Scrape" button:**

1. **Frontend** (`frontend/lib/api.ts`):
   ```typescript
   triggerScrape(sourceId) 
   → POST /api/scrape/{source_id}
   ```

2. **Backend API** (`app/api/routes/scrape.py`):
   ```python
   @router.post("/{source_id}")
   async def trigger_scrape(source_id, background_tasks)
   → background_tasks.add_task(scrape_source, source_id)
   ```

3. **Scraping Function** (`app/api/routes/scrape.py`):
   ```python
   async def scrape_source(source_id)
   → _scrape_source_sync(source_id)
   → Uses ScraperFactory to get the right scraper
   → Scrapes → Summarizes → Saves
   ```

**It's NOT calling the standalone scripts** (`scrape_aircargonews.py` or `scrape_aircargoweek.py`).  
It's calling the **same underlying code** but through the API.

## ⚠️ Current Limitations

### 1. No Progress Visibility
- Background tasks run silently
- No real-time progress updates
- Can't see how many articles are being processed

### 2. Can't Stop Running Scrapes
- FastAPI BackgroundTasks can't be easily cancelled
- Once started, it runs to completion
- No "Stop" button available

### 3. No Status Checking
- Can't see if scraping is still running
- Can't see if it completed successfully
- Have to check database manually

## ✅ Solutions Added

### 1. Check Scraping Status
```bash
# API endpoint
GET /api/scrape/status/{source_id}

# Returns:
{
  "status": "success" | "failed" | "partial" | "never_scraped",
  "articles_found": 90,
  "error_message": null,
  "created_at": "2025-11-13T16:20:00Z"
}
```

### 2. View Scraping Logs
```bash
# API endpoint
GET /api/scrape/logs/{source_id}?limit=10

# Returns list of recent scraping runs
```

### 3. Check in Supabase
- Go to `scraping_logs` table
- See all scraping history
- Check `status`, `articles_found`, `error_message`

## 🛑 How to Stop Scraping

**Unfortunately, FastAPI BackgroundTasks cannot be easily stopped once started.**

**Options:**
1. **Restart the backend server** (stops all background tasks)
   ```bash
   # Stop: Ctrl+C in terminal running uvicorn
   # Start: uvicorn app.main:app --reload
   ```

2. **Wait for completion** - It will finish on its own

3. **Kill the process** (not recommended)
   ```bash
   # Find process
   ps aux | grep uvicorn
   # Kill it
   kill <PID>
   ```

## 📊 How to Monitor Progress

### Option 1: Check Scraping Logs (Recommended)
1. Go to Supabase dashboard
2. Open `scraping_logs` table
3. Filter by `source_id`
4. Check latest log entry:
   - `status`: "success", "failed", or "partial"
   - `articles_found`: Total URLs found
   - `created_at`: When it finished

### Option 2: Check Articles Table
1. Go to Supabase dashboard
2. Open `articles` table
3. Filter by `source_id`
4. Sort by `created_at` DESC
5. See new articles appearing as they're processed

### Option 3: Use API Endpoints (New)
```bash
# Check status
curl http://localhost:8000/api/scrape/status/{source_id}

# View logs
curl http://localhost:8000/api/scrape/logs/{source_id}
```

## 💡 Recommendations

### For Testing/Debugging:
- **Use the standalone scripts** (`scrape_aircargonews.py` or `scrape_aircargoweek.py`)
- See real-time progress
- Can stop with Ctrl+C

### For Production/Daily Use:
- **Use the web button**
- Check status via API or Supabase
- Let it run in background
- Articles appear automatically

## 🔮 Future Improvements (Not Implemented Yet)

1. **Real-time Progress Updates**
   - WebSocket connection
   - Live progress bar
   - Article count updates

2. **Cancellation Support**
   - Task queue system (Celery, RQ)
   - Cancel button in UI
   - Graceful shutdown

3. **Progress Dashboard**
   - Show active scrapes
   - Progress percentage
   - Estimated time remaining

---

## Summary

**The "Scrape" button:**
- ✅ Calls `app/api/routes/scrape.py` → `scrape_source()` function
- ✅ Runs in background (non-blocking)
- ✅ Uses the same scraping code as standalone scripts
- ❌ No real-time progress (check logs instead)
- ❌ Can't be stopped easily (restart server if needed)
- ✅ Check status via API: `/api/scrape/status/{source_id}`
- ✅ View logs via API: `/api/scrape/logs/{source_id}`

