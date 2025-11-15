# 🔍 How to Check and Stop Running Scraping Scripts

## Method 1: Check Running Tasks via API (Recommended)

### Step 1: Check What's Running

**Option A: Via Browser/API Client**
```
GET https://web-production-1349.up.railway.app/api/scrape/running
```

**Option B: Via Terminal (curl)**
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
      "started_at": "2025-11-15T08:00:00",
      "status": "running"
    }
  ],
  "count": 1
}
```

---

### Step 2: Stop Running Tasks

**Stop Specific Source:**
```
POST https://web-production-1349.up.railway.app/api/scrape/stop/{source_id}
```

**Stop All Running Tasks:**
```
POST https://web-production-1349.up.railway.app/api/scrape/stop-all
```

**Example (curl):**
```bash
# Stop all
curl -X POST https://web-production-1349.up.railway.app/api/scrape/stop-all

# Stop specific source
curl -X POST https://web-production-1349.up.railway.app/api/scrape/stop/{source_id}
```

---

## Method 2: Restart Railway Service (Nuclear Option)

If the API endpoints don't work or tasks are stuck, restart the Railway service:

### Steps:

1. **Go to Railway Dashboard**
   - https://railway.app/dashboard

2. **Select Your Backend Service**
   - Click on the backend service (usually named "web" or "backend")

3. **Go to Settings Tab**
   - Click "Settings" in the top menu

4. **Restart Service**
   - Scroll down to "Danger Zone"
   - Click "Restart" button
   - OR click the "..." menu → "Restart"

5. **Wait for Restart**
   - Service will restart (30-60 seconds)
   - All running tasks will be killed
   - New requests will work normally

---

## Method 3: Check Railway Logs

### Steps:

1. **Go to Railway Dashboard**
   - Select your backend service

2. **Click "Deployments" Tab**
   - Or click "View Logs" button

3. **Look for These Messages:**
   - `🚀 Starting Air Cargo Week subprocess scraping` → Task started
   - `✅ Scraping task for {id} completed` → Task finished
   - `Starting scrape for source: {name}` → Thread task started

4. **Check for Stuck Tasks:**
   - If you see "Starting" but no "completed" for >30 minutes → Task is stuck
   - Look for error messages

---

## Quick Troubleshooting

### Webpage Stuck at Loading

**Possible Causes:**
1. Background scraping task is blocking the server
2. Too many concurrent requests
3. Database connection issues

**Solutions:**
1. **Check running tasks** (Method 1)
2. **Stop all tasks** if any are running
3. **Restart Railway service** (Method 2)
4. **Wait 1-2 minutes** for tasks to complete naturally

---

### How to Verify Tasks Stopped

After stopping tasks, check again:
```bash
curl https://web-production-1349.up.railway.app/api/scrape/running
```

Should return:
```json
{
  "running_tasks": [],
  "count": 0
}
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/scrape/running` | GET | List all running tasks |
| `/api/scrape/stop/{source_id}` | POST | Stop specific task |
| `/api/scrape/stop-all` | POST | Stop all running tasks |
| `/api/scrape/status/{source_id}` | GET | Get latest scraping status |

---

## Notes

- **Stopping tasks** will terminate them immediately (may leave partial data)
- **Restarting Railway** kills all processes (clean slate)
- **Tasks auto-remove** from tracking when they complete
- **Subprocess tasks** (Air Cargo Week) can be terminated via API
- **Thread pool tasks** can be cancelled via API

---

## If Nothing Works

1. **Restart Railway service** (Method 2) - This always works
2. **Check Railway logs** for errors
3. **Verify backend is running** (check health endpoint)
4. **Contact support** if issues persist

