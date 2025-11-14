# 🔄 Complete Flow: What Happens When You Click "Scrape" Button

## 📍 Step-by-Step Execution Flow

### **Step 1: User Clicks "Scrape" Button in Browser**

**Location:** `frontend/components/SourceList.tsx` (line 116-121)

```typescript
<button
  onClick={() => onScrape(source.id)}  // ← This is called
  className="px-3 py-1.5 bg-green-600..."
>
  Scrape
</button>
```

**What happens:**
- User clicks button
- React calls `onScrape(source.id)` function
- `source.id` = UUID like `"faea0d61-79a1-4fd4-847e-6ccf707f98d6"`

---

### **Step 2: Frontend Handler Function**

**Location:** `frontend/app/sources/page.tsx` (line 89-108)

```typescript
const handleScrapeSource = async (sourceId: string) => {
  // Shows confirmation dialog
  if (!confirm(`Start scraping ${sourceName}? ...`)) {
    return;
  }
  
  setScrapingSourceId(sourceId);  // Shows loading state
  try {
    const result = await triggerScrape(sourceId);  // ← API call
    alert(result.message || `Scraping started...`);
  } catch (err) {
    alert('Failed to start scraping: ' + err.message);
  } finally {
    setScrapingSourceId(null);
  }
};
```

**What happens:**
- Shows confirmation dialog
- Calls `triggerScrape(sourceId)` from API client
- Shows alert with result

---

### **Step 3: Frontend API Client**

**Location:** `frontend/lib/api.ts` (line 72-77)

```typescript
export async function triggerScrape(sourceId?: string) {
  const endpoint = sourceId 
    ? `/api/scrape/${sourceId}`  // ← Single source
    : '/api/scrape/all';          // ← All sources
  
  return request<any>(endpoint, {
    method: 'POST',  // ← HTTP POST request
  });
}
```

**What happens:**
- Builds API endpoint: `POST http://localhost:8000/api/scrape/{source_id}`
- Sends HTTP POST request to backend
- Waits for response

**Network Request:**
```
POST http://localhost:8000/api/scrape/faea0d61-79a1-4fd4-847e-6ccf707f98d6
Content-Type: application/json
```

---

### **Step 4: Backend API Route Handler**

**Location:** `app/api/routes/scrape.py` (line 172-188)

```python
@router.post("/{source_id}")
async def trigger_scrape(source_id: UUID, background_tasks: BackgroundTasks):
    """Manually trigger scraping for a specific source."""
    
    # Step 4a: Get source from database
    source = db.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Step 4b: Add scraping task to background queue
    background_tasks.add_task(scrape_source, source_id)  # ← Queues the task
    
    # Step 4c: Return immediately (doesn't wait for scraping to finish)
    return {
        "message": f"Scraping started for source: {source.name}",
        "source_id": str(source_id)
    }
```

**What happens:**
- Receives POST request
- Gets source from database (`app/database/supabase_client.py`)
- **Queues** `scrape_source()` function to run in background
- **Returns immediately** with "Scraping started" message
- **Does NOT wait** for scraping to complete

**Key Point:** The function returns in ~0.1 seconds, but scraping continues in background!

---

### **Step 5: Background Task Execution**

**Location:** `app/api/routes/scrape.py` (line 162-169)

```python
async def scrape_source(source_id: UUID):
    """
    Async wrapper that runs blocking operations in thread pool.
    """
    loop = asyncio.get_event_loop()
    # Runs _scrape_source_sync in a separate thread
    await loop.run_in_executor(None, _scrape_source_sync, source_id)
```

**What happens:**
- FastAPI's `BackgroundTasks` calls this function
- It runs `_scrape_source_sync()` in a **separate thread**
- This prevents blocking the web server

---

### **Step 6: Actual Scraping Function**

**Location:** `app/api/routes/scrape.py` (line 17-159)

```python
def _scrape_source_sync(source_id: UUID):
    """
    This is where the REAL scraping happens!
    Runs in background thread.
    """
    
    # Step 6a: Get source from database
    source = db.get_source(source_id)
    
    # Step 6b: Create scraper (factory selects the right one)
    scraper = ScraperFactory.create_scraper(source.url)
    # For aircargoweek.com → Creates AircargoweekScraper
    # For aircargonews.net → Creates AircargonewsScraper
    
    # Step 6c: Get listing URL
    listing_url = ScraperFactory.get_listing_url(source.url)
    
    # Step 6d: Extract article URLs
    article_urls = scraper.get_article_urls(listing_url, max_pages=3, ...)
    # This calls:
    # - AircargoweekScraper.get_article_urls() → Uses Playwright
    # - OR AircargonewsScraper.get_article_urls() → Uses requests
    
    # Step 6e: Process each article
    for article_url in article_urls:
        # Scrape article content
        article_data = scraper.scrape_article(article_url)
        
        # Generate AI summary
        summary_data = summarizer.summarize(...)
        
        # Save to database
        db.create_article(article)
    
    # Step 6f: Create scraping log
    db.create_scraping_log(...)
```

**What happens:**
- This is the **same code** that standalone scripts use
- But it's called through the API, not directly
- Runs in background thread (you don't see output)
- Takes 5-30 minutes depending on articles

---

## 🔍 Key Files Involved

### **Frontend (Browser):**
1. `frontend/components/SourceList.tsx` - Button component
2. `frontend/app/sources/page.tsx` - Handler function
3. `frontend/lib/api.ts` - API client (HTTP request)

### **Backend (Server):**
4. `app/main.py` - FastAPI app (receives HTTP request)
5. `app/api/routes/scrape.py` - API route handler
6. `app/api/routes/scrape.py` - `_scrape_source_sync()` function
7. `app/scraper/scraper_factory.py` - Selects scraper
8. `app/scraper/aircargoweek_scraper.py` - OR `aircargonews_scraper.py`
9. `app/ai/summarizer.py` - AI summarization
10. `app/database/supabase_client.py` - Database operations

---

## 🆚 Comparison: Direct Script vs Web Button

### **When You Run Script Directly:**
```bash
python3 scrape_aircargoweek.py
```

**Flow:**
```
Terminal → scrape_aircargoweek.py
         → get_or_create_source()
         → scrape_aircargoweek()  # Same as _scrape_source_sync
         → ScraperFactory.create_scraper()
         → AircargoweekScraper.get_article_urls()
         → Scrape articles...
         → Print progress to terminal ✅
```

**You see:** Real-time output in terminal

---

### **When You Click Web Button:**
```
Browser → Frontend API call
       → Backend API route
       → Background task queue
       → _scrape_source_sync()  # Same function!
       → ScraperFactory.create_scraper()
       → AircargoweekScraper.get_article_urls()
       → Scrape articles...
       → (No output visible) ❌
```

**You see:** Nothing (runs silently in background)

---

## 🏠 Local vs Railway Deployment

### **Local (Your Computer):**

**Backend Server:**
```bash
uvicorn app.main:app --reload --port 8000
```
- Runs on: `http://localhost:8000`
- Background tasks run in same process
- Can see logs in terminal
- Can restart to stop tasks

**Frontend:**
```bash
cd frontend && npm run dev
```
- Runs on: `http://localhost:3000`
- Connects to `http://localhost:8000`

**Flow:**
```
Browser (localhost:3000)
    ↓ HTTP POST
FastAPI (localhost:8000)
    ↓ Background task
Scraping runs in same process
    ↓
Supabase (cloud database)
```

---

### **Railway (Online Deployment):**

**Backend Server:**
- Railway runs: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Runs on: `https://your-app.railway.app`
- Background tasks run in same process
- Logs visible in Railway dashboard
- Can restart service to stop tasks

**Frontend:**
- Railway runs: `npm run build && npm start`
- Runs on: `https://your-frontend.railway.app`
- Connects to backend URL

**Flow:**
```
Browser (your-frontend.railway.app)
    ↓ HTTP POST
FastAPI (your-backend.railway.app)
    ↓ Background task
Scraping runs in Railway server
    ↓
Supabase (cloud database)
```

**Differences:**
- ✅ Same code, same flow
- ✅ Works the same way
- ✅ Background tasks work identically
- ⚠️ Can't see terminal output (check Railway logs)
- ⚠️ Can't easily stop (restart Railway service)

---

## 📊 Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User clicks "Scrape" button                        │
│ File: frontend/components/SourceList.tsx                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Frontend handler                                    │
│ File: frontend/app/sources/page.tsx                         │
│ Function: handleScrapeSource(sourceId)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: API client makes HTTP request                       │
│ File: frontend/lib/api.ts                                   │
│ Function: triggerScrape(sourceId)                           │
│ Request: POST http://localhost:8000/api/scrape/{source_id}  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Backend receives request                            │
│ File: app/api/routes/scrape.py                              │
│ Function: trigger_scrape(source_id, background_tasks)        │
│ Action: background_tasks.add_task(scrape_source, source_id)│
│ Returns: {"message": "Scraping started..."}                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (Returns immediately to browser)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Background task starts                              │
│ File: app/api/routes/scrape.py                             │
│ Function: scrape_source(source_id)                          │
│ Action: Runs _scrape_source_sync() in thread pool           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Actual scraping happens                            │
│ File: app/api/routes/scrape.py                              │
│ Function: _scrape_source_sync(source_id)                    │
│                                                              │
│ 6a. Get source from database                                │
│ 6b. ScraperFactory.create_scraper()                         │
│     → Creates AircargoweekScraper or AircargonewsScraper    │
│ 6c. scraper.get_article_urls()                              │
│     → File: app/scraper/aircargoweek_scraper.py            │
│     → Uses Playwright to extract URLs                       │
│ 6d. For each URL:                                           │
│     - scraper.scrape_article()                              │
│     - summarizer.summarize()                                │
│       → File: app/ai/summarizer.py                          │
│       → Calls Google Gemini API                             │
│     - db.create_article()                                   │
│       → File: app/database/supabase_client.py               │
│       → Saves to Supabase                                   │
│ 6e. db.create_scraping_log()                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Differences

### **Standalone Script (`scrape_aircargoweek.py`):**
- ✅ Runs directly in terminal
- ✅ Shows real-time progress
- ✅ Can stop with Ctrl+C
- ✅ No server needed
- ❌ Must run manually

### **Web Button:**
- ✅ Runs through API
- ✅ Can trigger from anywhere
- ✅ Runs in background (non-blocking)
- ✅ Same scraping code
- ❌ No visible progress (check logs/status)
- ❌ Can't easily stop (restart server)

---

## 💡 Why You Don't See Progress

**The scraping happens in a background thread:**
- Browser gets response immediately (~0.1 seconds)
- Scraping continues in background (5-30 minutes)
- No connection between browser and background task
- Progress is logged to server logs, not sent to browser

**To see progress:**
1. **Check server logs** (terminal running uvicorn)
2. **Check Supabase** (`scraping_logs` table)
3. **Check Sources page** (shows last status, auto-refreshes)
4. **Use API:** `GET /api/scrape/status/{source_id}`

---

## 🎯 Summary

**When you click "Scrape" button:**

1. **Frontend** sends HTTP POST to backend
2. **Backend** queues scraping task in background
3. **Backend** returns immediately ("Scraping started")
4. **Background thread** runs `_scrape_source_sync()`
5. **Scraper** (same as standalone script) does the work
6. **Results** saved to Supabase
7. **Status** visible in Sources page or logs

**It's the SAME scraping code**, just called through the API instead of directly!

