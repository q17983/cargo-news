# 🔄 How Scraping Works - Complete Guide

## What Happens When You Press "Scrape" Button

### For Air Cargo Week (Special Case)

1. **Frontend:** Button click → `POST /api/scrape/{source_id}`
2. **Backend Detection:**
   - Checks if source URL contains `aircargoweek.com`
   - If yes → Uses subprocess method (avoids Playwright threading issues)
3. **Subprocess Execution:**
   - Runs `scrape_aircargoweek.py` as separate process
   - Passes environment variables (GEMINI_API_KEY, SUPABASE_URL, etc.)
   - Runs with `--max-pages 5` (first-time scrape limit)
4. **Scraping Process:**
   - Launches Playwright browser
   - Navigates to listing page
   - Clicks "Load more" button to get articles
   - Extracts article URLs
   - For each article:
     - Scrapes content
     - Generates AI summary (Gemini API)
     - Checks for duplicates
     - Saves to Supabase
5. **Completion:**
   - Process exits
   - Scraping log created in database
   - Status updated

### For Other Sources (Air Cargo News, STAT Times)

1. **Frontend:** Button click → `POST /api/scrape/{source_id}`
2. **Backend:**
   - Uses thread pool executor
   - Runs scraper in background thread
3. **Scraping Process:**
   - Uses requests/Playwright fallback
   - Extracts article URLs from listing pages
   - For each article:
     - Scrapes content
     - Generates AI summary
     - Checks duplicates
     - Saves to Supabase
4. **Completion:**
   - Thread completes
   - Scraping log created
   - Status updated

---

## 📊 How to Check Progress

### Method 1: Web Interface (Real-Time)

**On Sources Page:**

1. **Status Column:**
   - Shows "🔄 Scraping..." badge when task is running
   - Shows start time
   - Updates every 3 seconds when scraping is active

2. **Actions Column:**
   - "Scrape" button changes to "⏹ Stop" when running
   - Click "Stop" to cancel the task

3. **Top Buttons:**
   - "Scrape All Sources" - Starts scraping for all sources
   - "⏹ Stop All" - Stops all running tasks

**Auto-Refresh:**
- Every 3 seconds when tasks are running
- Every 10 seconds when no tasks running

### Method 2: API Endpoints

**Check Running Tasks:**
```bash
curl https://web-production-1349.up.railway.app/api/scrape/running
```

**Response:**
```json
{
  "running_tasks": [
    {
      "source_id": "uuid-here",
      "source_name": "Air Cargo Week",
      "started_at": "2025-11-15T10:30:00",
      "status": "running"
    }
  ],
  "count": 1
}
```

**Check Latest Status:**
```bash
curl https://web-production-1349.up.railway.app/api/scrape/status/{source_id}
```

**Response:**
```json
{
  "source_id": "uuid-here",
  "status": "success",
  "articles_found": 25,
  "articles_processed": 20,
  "error_message": null,
  "created_at": "2025-11-15T10:35:00"
}
```

### Method 3: Railway Logs

1. Go to Railway Dashboard
2. Select Backend Service
3. Click "Deployments" → Latest → View Logs
4. Look for:
   - `🚀 Starting Air Cargo Week subprocess scraping`
   - `✅ Scraping task for {id} completed`
   - `Starting scrape for source: {name}`

### Method 4: Supabase Database

**Check Scraping Logs:**
```sql
SELECT * FROM scraping_logs 
WHERE source_id = 'your-source-id' 
ORDER BY created_at DESC 
LIMIT 10;
```

**Check Articles:**
```sql
SELECT COUNT(*) as total, 
       source_id,
       MAX(created_at) as latest
FROM articles 
GROUP BY source_id;
```

---

## ⏹️ How to Stop Scraping

### Method 1: Stop Button (Web Interface)

**For Single Source:**
1. Go to Sources page
2. Find the source that's scraping
3. Click "⏹ Stop" button
4. Confirm the action

**For All Sources:**
1. Click "⏹ Stop All" button at top
2. Confirm the action
3. All running tasks will be stopped

### Method 2: API Endpoints

**Stop Specific Source:**
```bash
curl -X POST https://web-production-1349.up.railway.app/api/scrape/stop/{source_id}
```

**Stop All:**
```bash
curl -X POST https://web-production-1349.up.railway.app/api/scrape/stop-all
```

### Method 3: Restart Railway Service

**Nuclear Option:**
1. Railway Dashboard → Backend Service
2. Settings → Restart
3. This kills ALL processes (including scraping)

---

## 🔍 Progress Indicators

### Visual Indicators

**In Web Interface:**
- 🔄 **Blue pulsing badge** = Currently scraping
- ✅ **Green checkmark** = Last scrape successful
- ❌ **Red X** = Last scrape failed
- ⚠️ **Yellow warning** = Partial success or warning

**Status Messages:**
- "🔄 Scraping..." = Task is running
- "Started: HH:mm:ss" = When scraping started
- "Last: ✅ 25 articles (Nov 15, 10:30)" = Last completed scrape

### What Gets Updated

**Real-Time (Every 3 seconds when scraping):**
- Running tasks list
- Start time
- Status badge

**After Completion:**
- Articles found count
- Success/failure status
- Error messages (if any)
- Completion timestamp

---

## ⚠️ Troubleshooting

### Scraping Stuck / Not Progressing

**Symptoms:**
- Status shows "🔄 Scraping..." for >30 minutes
- No new articles appearing
- Page stuck at loading

**Solutions:**
1. **Check Running Tasks:**
   - Click "⏹ Stop" button
   - Or use API: `GET /api/scrape/running`

2. **Check Railway Logs:**
   - Look for errors or timeouts
   - Check if Playwright is hanging

3. **Stop and Restart:**
   - Click "⏹ Stop" button
   - Wait a few seconds
   - Try scraping again

4. **Restart Backend:**
   - Railway → Backend Service → Settings → Restart
   - This kills all processes

### Scraping Fails Immediately

**Check:**
1. **API Key:** Is Gemini API key valid?
2. **Database:** Can backend connect to Supabase?
3. **Network:** Is the source website accessible?
4. **IP Block:** Is your IP blocked? (Check for 403 errors)

**Solutions:**
- Check error message in status
- Check Railway logs for details
- Verify environment variables are set

### No Progress Updates

**If status doesn't update:**
1. **Check Browser Console:**
   - Look for API errors
   - Check if requests are failing

2. **Check Network Tab:**
   - Verify `/api/scrape/running` requests are succeeding
   - Check response status codes

3. **Hard Refresh:**
   - `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - This clears cached JavaScript

---

## 📝 Best Practices

1. **Monitor Progress:**
   - Keep Sources page open to see real-time updates
   - Check status every few minutes

2. **Stop if Stuck:**
   - If scraping takes >30 minutes, stop it
   - Check logs to see what went wrong
   - Try again after fixing the issue

3. **Check Before Scraping:**
   - Verify source is active
   - Check last scrape status
   - Look for error messages

4. **Use Stop Button:**
   - Don't just close the browser
   - Use "⏹ Stop" to properly cancel tasks
   - This prevents orphaned processes

---

## 🎯 Quick Reference

| Action | Method | Result |
|--------|--------|--------|
| Start scraping | Click "Scrape" button | Starts background task |
| Check progress | View Sources page | Real-time status updates |
| Stop single source | Click "⏹ Stop" button | Cancels that task |
| Stop all | Click "⏹ Stop All" | Cancels all tasks |
| Check running | API: `GET /api/scrape/running` | List of active tasks |
| Check status | View status column | Last scrape result |

---

**Last Updated:** 2025-11-15

