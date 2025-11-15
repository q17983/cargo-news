# 🔍 Debug: Still Failing to Load Articles

## Step-by-Step Debugging

### Step 1: Check Browser Console (CRITICAL)

1. **Press F12** in your browser
2. **Go to "Console" tab**
3. **Look for red error messages**
4. **Copy and share the exact error message**

**Common errors:**
- `Failed to fetch` → Connection issue
- `CORS policy` → CORS issue
- `NetworkError` → Network issue
- `404 Not Found` → Wrong API URL
- `500 Internal Server Error` → Backend error

---

### Step 2: Check Network Tab

1. **Press F12** → **"Network" tab**
2. **Clear the network log** (trash icon)
3. **Refresh the page** (F5)
4. **Look for API requests**:
   - Should see: `/api/articles` or similar
   - Click on it to see details

**What to check:**
- **Request URL**: What URL is it trying to call?
- **Status**: 200 (OK), 404 (Not Found), 500 (Error), Failed?
- **Response**: What does the response say?

**Share:**
- The exact URL being called
- The status code
- The response (if any)

---

### Step 3: Test Backend API Directly

1. **Open a new browser tab**
2. **Visit**: `https://web-production-1349.up.railway.app/api/articles`
3. **What do you see?**
   - `[]` (empty array) → Backend works, just no articles
   - Error message → Backend issue
   - Nothing/CORS error → CORS issue

**Share what you see!**

---

### Step 4: Verify Environment Variable in Build

The variable might not be included in the build. Let's verify:

1. **Go to Railway → Frontend Service → Deployments**
2. **Click on latest deployment**
3. **Check "Logs" tab**
4. **Look for**: Does it show the variable being used?

**Or test in browser:**
1. **Press F12** → **Console tab**
2. **Type**: `console.log(process.env.NEXT_PUBLIC_API_URL)`
3. **Press Enter**
4. **What does it show?**
   - `undefined` → Variable not included in build
   - `https://web-production-1349.up.railway.app` → Variable is set
   - `http://localhost:8000` → Using default (wrong!)

---

### Step 5: Check CORS Configuration

If you see CORS errors:

1. **Backend should have CORS enabled** (already configured)
2. **Check backend logs** in Railway
3. **Verify CORS allows your frontend domain**

---

## Most Likely Issues

### Issue 1: Variable Not in Build (Most Likely)
**Symptom**: Console shows `undefined` or `http://localhost:8000`

**Fix:**
1. Double-check variable name: `NEXT_PUBLIC_API_URL` (exact spelling!)
2. Make sure it's set in **Frontend Service** Variables (not just project)
3. Redeploy again
4. Wait for build to complete

### Issue 2: CORS Error
**Symptom**: Console shows CORS policy error

**Fix:**
- Backend should allow all origins (already configured)
- Check backend logs for CORS errors

### Issue 3: Wrong API URL
**Symptom**: 404 Not Found

**Fix:**
- Verify backend URL is correct
- Test backend health: `https://web-production-1349.up.railway.app/health`

### Issue 4: Backend Not Running
**Symptom**: Connection refused, timeout

**Fix:**
- Check backend service status in Railway
- Check backend deployment logs

---

## Quick Diagnostic Commands

**In Browser Console (F12):**
```javascript
// Check if variable is set
console.log(process.env.NEXT_PUBLIC_API_URL)

// Try to fetch directly
fetch('https://web-production-1349.up.railway.app/api/articles')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**Share the output!**

---

## What I Need From You

Please share:

1. **Browser console error** (F12 → Console → copy the red error)
2. **Network tab details** (F12 → Network → click on `/api/articles` → share Status, URL, Response)
3. **Direct API test result**: What do you see at `https://web-production-1349.up.railway.app/api/articles`?
4. **Environment variable check**: What does `console.log(process.env.NEXT_PUBLIC_API_URL)` show in browser console?

This will help me identify the exact issue!

