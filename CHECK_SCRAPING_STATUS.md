# 🔍 Check Scraping Status on Railway

## Step 1: Check Deployment Logs (Verify Fix Applied)

### Backend Service:
1. **Go to Railway Dashboard**
2. **Click on your Backend Service**
3. **Go to "Deployments" tab**
4. **Click on the latest deployment**
5. **Check "Logs" tab**
6. **Look for**: The deployment should complete successfully
7. **Verify**: No errors about `--check-duplicates`

---

## Step 2: Monitor Scraping Process

### After Pressing "Scrape" Button:

1. **Go to Backend Service → "Logs" tab** (or "Deployments" → Latest → "Logs")
2. **Watch for these messages**:

**✅ Good Signs:**
- `Using subprocess for Air Cargo Week (Playwright compatibility)`
- `Running Air Cargo Week scraper via subprocess: ...`
- `Starting scraping for Air Cargo Week...`
- `Found X articles on page Y`
- `Processing article: ...`
- `Article saved successfully`
- `Air Cargo Week scraping completed successfully`

**❌ Bad Signs:**
- `unrecognized arguments: --check-duplicates` → Fix not applied (need redeploy)
- `Script not found at: ...` → Path issue
- `403 FORBIDDEN` → IP blocked
- `quota exceeded` → OpenAI API quota issue
- `Subprocess failed` → Check error details

---

## Step 3: Check Frontend Status

### In the Webpage:
1. **Go to Sources page** (`/sources`)
2. **Look at the status column** for your Air Cargo Week source
3. **Should show**:
   - Latest scraping status
   - Number of articles found
   - Timestamp
   - Any error messages (in red)

### Refresh Status:
- The status updates automatically every 10 seconds
- Or refresh the page manually

---

## Step 4: Check Database (Supabase)

1. **Go to Supabase Dashboard**
2. **Go to Table Editor**
3. **Check `articles` table**:
   - Should see new articles appearing
   - Filter by source to see Air Cargo Week articles
4. **Check `scraping_logs` table**:
   - Should see latest log entry
   - Check `status` (success/failed/partial)
   - Check `articles_found` and `articles_processed`

---

## Step 5: Common Issues & Solutions

### Issue 1: Still Seeing `--check-duplicates` Error
**Solution:**
- Backend might not have redeployed yet
- Wait a few more minutes
- Check deployment status (should be "Active")
- Try scraping again

### Issue 2: Script Not Found
**Solution:**
- Verify `scrape_aircargoweek.py` exists in project root
- Check Railway build logs to see if file was copied
- Path fix should be in latest deployment

### Issue 3: 403 Forbidden (IP Blocked)
**Solution:**
- Air Cargo Week is blocking Railway's IP
- This is a known issue
- May need to wait or use different approach

### Issue 4: No Logs Appearing
**Solution:**
- Check if backend service is running
- Check deployment status
- Verify backend URL is correct

---

## Quick Diagnostic Commands

### Check Backend Health:
Visit: `https://web-production-1349.up.railway.app/health`
Should see: `{"status": "healthy"}`

### Check Latest Scraping Logs:
Visit: `https://web-production-1349.up.railway.app/api/scrape/logs/{source_id}`
(Replace `{source_id}` with your Air Cargo Week source ID)

---

## What to Share

If scraping is still not working, please share:

1. **Backend Logs** (from Railway → Backend → Logs)
   - Last 20-30 lines after pressing scrape
   - Any error messages

2. **Frontend Status** (from Sources page)
   - What status is shown?
   - Any error messages?

3. **Deployment Status**
   - Is backend deployment "Active"?
   - When was it last deployed?

This will help identify the exact issue!

