# 🔍 Debug Frontend Loading Issue

## Current Status
- ✅ Backend is healthy: `{"status":"healthy"}`
- ❌ Frontend stuck at "Loading articles..." and "Loading sources..."

## Quick Debug Steps

### Step 1: Check Browser Console

1. **Open Browser Console:**
   - Press `F12` or `Right-click → Inspect → Console tab`

2. **Look for Errors:**
   - Red error messages
   - Network errors
   - CORS errors
   - Timeout errors

3. **Check API URL:**
   ```javascript
   // In console, type:
   console.log('API_URL:', process.env.NEXT_PUBLIC_API_URL);
   ```
   - Should show: `https://web-production-1349.up.railway.app`
   - If `undefined` or `http://localhost:8000` → Frontend not deployed with correct env var

---

### Step 2: Check Network Tab

1. **Open Network Tab:**
   - DevTools → Network tab
   - Reload page (F5)

2. **Look for API Requests:**
   - `/api/articles` - Should return 200 OK
   - `/api/sources` - Should return 200 OK
   - `/api/articles/tags/list` - Should return 200 OK

3. **Check Request Status:**
   - **Pending (forever)** → Backend not responding or timeout
   - **Failed (CORS error)** → CORS configuration issue
   - **Failed (404)** → Wrong API URL
   - **Failed (500)** → Backend error

---

### Step 3: Test API Endpoints Directly

**In Browser Console, try:**

```javascript
// Test articles endpoint
fetch('https://web-production-1349.up.railway.app/api/articles?limit=10')
  .then(r => r.json())
  .then(data => console.log('Articles:', data))
  .catch(err => console.error('Error:', err));

// Test sources endpoint
fetch('https://web-production-1349.up.railway.app/api/sources')
  .then(r => r.json())
  .then(data => console.log('Sources:', data))
  .catch(err => console.error('Error:', err));
```

**Expected Results:**
- ✅ Should return arrays of data
- ❌ If error → Check error message

---

### Step 4: Check Railway Environment Variables

**Frontend Service in Railway:**

1. Go to Railway Dashboard
2. Select **Frontend Service**
3. Go to **Variables** tab
4. Check `NEXT_PUBLIC_API_URL`:
   - Should be: `https://web-production-1349.up.railway.app`
   - If missing or wrong → Add/Update it
   - **Important:** After changing, Railway will auto-redeploy

---

### Step 5: Verify Frontend Deployment

**Check if timeout fixes are deployed:**

1. **Check Railway Deployments:**
   - Frontend service → Deployments tab
   - Look for recent deployment (should be after the timeout fix commit)

2. **Check Build Logs:**
   - Look for any build errors
   - Should see "Build successful"

3. **Force Redeploy:**
   - If unsure, trigger manual redeploy:
   - Settings → Redeploy

---

## Common Issues & Solutions

### Issue 1: API URL Not Set
**Symptom:** Console shows `API_URL: undefined` or `http://localhost:8000`

**Solution:**
1. Railway → Frontend Service → Variables
2. Add/Update: `NEXT_PUBLIC_API_URL = https://web-production-1349.up.railway.app`
3. Wait for redeploy (2-3 minutes)

---

### Issue 2: CORS Error
**Symptom:** Console shows "CORS policy" error

**Solution:**
- Backend already allows all origins (`allow_origins=["*"]`)
- If still seeing CORS error, check backend logs

---

### Issue 3: Requests Timing Out
**Symptom:** Network tab shows requests pending for >30 seconds

**Solution:**
- Timeout fixes should handle this (30-second timeout)
- If still timing out, backend might be slow
- Check backend logs in Railway

---

### Issue 4: 404 Not Found
**Symptom:** Network tab shows 404 for API requests

**Solution:**
- Check API URL is correct
- Verify backend is running
- Check Railway backend service status

---

### Issue 5: 500 Server Error
**Symptom:** Network tab shows 500 for API requests

**Solution:**
- Check backend logs in Railway
- Look for error messages
- Verify database connection

---

## Quick Test Commands

**Test Backend Health:**
```bash
curl https://web-production-1349.up.railway.app/health
# Should return: {"status":"healthy"}
```

**Test Articles Endpoint:**
```bash
curl https://web-production-1349.up.railway.app/api/articles?limit=5
# Should return JSON array
```

**Test Sources Endpoint:**
```bash
curl https://web-production-1349.up.railway.app/api/sources
# Should return JSON array
```

---

## What to Share

If still stuck, share:

1. **Browser Console Errors** (screenshot or copy-paste)
2. **Network Tab** - Failed requests (screenshot)
3. **API Test Results** - What the fetch commands return
4. **Railway Logs** - Backend service logs

This will help identify the exact issue!

