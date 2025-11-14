# Scraping Methods Comparison

## Method 1: Running Script Directly (`scrape_aircargoweek.py`)

### How it works:
```bash
python3 scrape_aircargoweek.py --max-pages 3
```

### Characteristics:
- ✅ **Direct execution** - Runs immediately in your terminal
- ✅ **Synchronous** - You see output in real-time as it processes
- ✅ **Interactive** - You can see progress, errors, and results immediately
- ✅ **No server needed** - Works without FastAPI backend running
- ✅ **Full control** - You can stop it (Ctrl+C) anytime
- ✅ **Command-line arguments** - Easy to customize (--max-pages, --no-duplicate-check)
- ✅ **Perfect for testing** - Great for debugging and development
- ✅ **Can be scheduled** - Can be added to cron jobs for automation

### Output:
```
======================================================================
Air Cargo Week - Complete Scraping Workflow
======================================================================

Source: Air Cargo Week
Source ID: faea0d61-79a1-4fd4-847e-6ccf707f98d6

Listing URL: https://aircargoweek.com/news/

Step 1: Extracting article URLs...
----------------------------------------------------------------------
✓ Found 90 article URLs

Step 2: Processing 90 articles...
----------------------------------------------------------------------

[1/90] Processing: https://aircargoweek.com/dhl-global-forwarding...
   🤖 Generating AI summary...
   ✓ Saved to database

[2/90] Processing: https://aircargoweek.com/rhenus-strengthens...
   🤖 Generating AI summary...
   ✓ Saved to database
...
```

### When to use:
- Testing the scraper
- Debugging issues
- Running one-time scrapes
- Setting up cron jobs
- When you want to see real-time progress

---

## Method 2: Clicking "Scrape" Button in Web Interface

### How it works:
1. Click "Scrape" button next to a source
2. Frontend calls: `POST /api/scrape/{source_id}`
3. Backend starts scraping as a **background task**
4. Returns immediately with "Scraping started" message
5. Processing happens in the background

### Characteristics:
- ✅ **Asynchronous** - Returns immediately, doesn't block the web page
- ✅ **Background processing** - Runs in the background while you can use the site
- ✅ **No terminal needed** - Works from anywhere (web browser, mobile, etc.)
- ✅ **User-friendly** - Simple click, no command-line knowledge needed
- ✅ **Server required** - Needs FastAPI backend running
- ✅ **No real-time output** - You don't see progress in terminal
- ✅ **Check results later** - Articles appear in web interface when done
- ✅ **Multiple sources** - Can scrape all sources at once with "Scrape All Sources"

### Flow:
```
User clicks "Scrape" button
    ↓
Frontend: POST /api/scrape/{source_id}
    ↓
Backend: background_tasks.add_task(scrape_source, source_id)
    ↓
Returns: {"message": "Scraping started..."}
    ↓
[Background] Scraping happens...
    ↓
Articles appear in web interface
```

### When to use:
- Daily operations
- Non-technical users
- When you want to use the web interface
- When scraping multiple sources
- When you don't need to see real-time progress

---

## Key Differences Summary

| Feature | Script Direct | Web Button |
|---------|--------------|------------|
| **Execution** | Synchronous (blocking) | Asynchronous (non-blocking) |
| **Output** | Real-time in terminal | No visible output |
| **Server needed** | ❌ No | ✅ Yes (FastAPI) |
| **User interface** | Terminal/Command line | Web browser |
| **Progress visibility** | ✅ Yes (real-time) | ❌ No (check results later) |
| **Stopping** | Ctrl+C | Can't stop easily |
| **Scheduling** | ✅ Easy (cron) | Via scheduler in code |
| **Multiple sources** | Run script multiple times | "Scrape All" button |
| **Best for** | Testing, debugging | Production, daily use |

---

## What They Share

Both methods:
- ✅ Use the **same underlying code** (`scrape_source` function)
- ✅ Do the **same thing**: scrape → summarize → save to Supabase
- ✅ Check for duplicates
- ✅ Generate AI summaries
- ✅ Save to the same database
- ✅ Create scraping logs

---

## Recommendation

- **For testing/debugging**: Use the script directly
- **For daily operations**: Use the web button
- **For automation**: Use the script in cron jobs OR use the built-in scheduler (runs daily at 00:00 UTC)

