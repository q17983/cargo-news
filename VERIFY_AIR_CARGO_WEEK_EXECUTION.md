# 🔍 Verify Air Cargo Week Script Execution

## How Backend Detects and Runs Air Cargo Week

### Detection Logic

1. **When "Scrape" button is clicked**:
   - Frontend calls: `POST /api/scrape/{source_id}`
   - Or: `POST /api/scrape/all` (for all sources)

2. **Backend checks source URL**:
   ```python
   source = db.get_source(source_id)
   if 'aircargoweek.com' in source.url.lower():
       # Use subprocess
   ```

3. **If Air Cargo Week detected**:
   - Calls `_scrape_via_subprocess(source_id)`
   - Runs `scrape_aircargoweek.py` as subprocess
   - Passes environment variables (including `OPENAI_API_KEY`)

---

## How to Verify It's Running

### Step 1: Check Railway Backend Logs

After clicking "Scrape" for Air Cargo Week, look for these log messages:

**✅ Detection Messages:**
```
🔍 Checking source: Air Cargo Week | URL: https://aircargoweek.com/news/
✅ Detected Air Cargo Week source - Using subprocess (Playwright compatibility)
   Source ID: <uuid>
   Source URL: https://aircargoweek.com/news/
```

**✅ Subprocess Start:**
```
🚀 Starting Air Cargo Week subprocess scraping for source: <uuid>
🔍 Current file location: /app/app/api/routes/scrape.py
✅ Found script at: /app/scrape_aircargoweek.py (Railway root - priority 1)
Passing environment variables to subprocess (OPENAI_API_KEY present: True)
Running Air Cargo Week scraper via subprocess: /opt/venv/bin/python /app/scrape_aircargoweek.py
```

**✅ Script Execution:**
```
Air Cargo Week - Complete Scraping Workflow
==========================================
Source: Air Cargo Week
Starting scraping for Air Cargo Week...
```

**❌ If NOT Running:**
- No "Detected Air Cargo Week" message → Detection failed
- No "Starting Air Cargo Week subprocess" → Subprocess not called
- "Script not found" → Path issue

---

### Step 2: Verify Source URL in Database

The detection depends on the source URL containing `aircargoweek.com`.

**Check in Supabase:**
1. Go to Supabase Dashboard
2. Table Editor → `news_sources` table
3. Find Air Cargo Week source
4. Check the `url` column:
   - ✅ Should contain: `aircargoweek.com`
   - ❌ If wrong URL → Detection won't work

**Common URLs:**
- ✅ `https://aircargoweek.com/news/`
- ✅ `https://www.aircargoweek.com/news/`
- ✅ `aircargoweek.com/news/`
- ❌ Wrong domain → Won't detect

---

### Step 3: Check Subprocess Output

The subprocess should output to logs. Look for:
- Script startup messages
- "Found X articles" messages
- Any error messages from the script

---

## Common Issues

### Issue 1: Detection Not Working
**Symptom**: No "Detected Air Cargo Week" message

**Possible Causes:**
- Source URL doesn't contain `aircargoweek.com`
- Source not found in database
- URL has typo

**Fix:**
- Check source URL in Supabase
- Verify it contains `aircargoweek.com` (case-insensitive)

### Issue 2: Subprocess Not Starting
**Symptom**: "Detected" message but no subprocess start

**Possible Causes:**
- Exception in `_scrape_via_subprocess`
- Path calculation failed

**Fix:**
- Check logs for error messages
- Verify script path is correct

### Issue 3: Script Not Found
**Symptom**: "Script not found" error

**Possible Causes:**
- File not in Railway deployment
- Wrong path calculation

**Fix:**
- Verify `scrape_aircargoweek.py` is in Git
- Check Railway build logs for file copying

---

## Quick Verification Checklist

- [ ] Source URL in database contains `aircargoweek.com`
- [ ] Backend logs show "Detected Air Cargo Week" message
- [ ] Backend logs show "Starting Air Cargo Week subprocess"
- [ ] Backend logs show "Found script at: /app/scrape_aircargoweek.py"
- [ ] Backend logs show "OPENAI_API_KEY present: True"
- [ ] Script starts executing (see script output in logs)
- [ ] No "Script not found" errors
- [ ] No path errors

---

## What to Share

If it's still not working, share:

1. **Backend logs** after clicking "Scrape" for Air Cargo Week:
   - Look for detection messages
   - Look for subprocess start messages
   - Look for any errors

2. **Source URL from Supabase**:
   - What is the exact URL stored in database?

3. **Any error messages** from the logs

This will help identify if it's a detection issue, path issue, or execution issue!

