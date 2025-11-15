# 🔍 Debug: "Loading articles..." Issue

## Problem
Page shows "Loading articles..." but never loads. This means the frontend can't connect to the backend API.

---

## Step 1: Check Browser Console (CRITICAL)

1. **Press F12** in your browser
2. **Go to "Console" tab**
3. **Look for red error messages**

**Common errors you might see:**
- `Failed to fetch` → Backend not connected
- `NetworkError` → Backend is down
- `CORS error` → CORS configuration issue
- `NEXT_PUBLIC_API_URL is not defined` → Environment variable missing

**Please share what errors you see!**

---

## Step 2: Check Network Tab

1. **Press F12** → **"Network" tab**
2. **Refresh the page** (F5)
3. **Look for API calls**:
   - Should see: `/api/articles` or similar
   - Check if it shows **200 (OK)** or **Failed/Error**
   - Click on the request to see details

**What to look for:**
- ✅ **200 OK** → Backend is working, but no articles (expected if database is empty)
- ❌ **Failed** → Backend connection issue
- ❌ **CORS error** → CORS configuration problem

---

## Step 3: Verify Environment Variable

### In Railway Dashboard:

1. **Go to Railway Dashboard**
2. **Click on your Frontend Service**
3. **Go to "Variables" tab**
4. **Check if you have**:
   ```
   NEXT_PUBLIC_API_URL = https://web-production-1349.up.railway.app
   ```

**If missing:**
1. Click **"+ New Variable"**
2. **Name**: `NEXT_PUBLIC_API_URL`
3. **Value**: `https://web-production-1349.up.railway.app` (NO trailing slash!)
4. **Save** → Railway will redeploy automatically

**If wrong:**
1. Click on the variable
2. Update the value
3. Save → Railway will redeploy

---

## Step 4: Test Backend Directly

1. **Open a new browser tab**
2. **Visit**: `https://web-production-1349.up.railway.app/health`
3. **Should see**: `{"status": "healthy"}`

**If this doesn't work:**
- Backend service might be down
- Check backend service in Railway
- Check backend deployment logs

---

## Step 5: Test API Endpoint

1. **Visit**: `https://web-production-1349.up.railway.app/api/articles`
2. **Should see**: `[]` (empty array) or a list of articles

**If you see an error:**
- Backend API is not working
- Check backend logs in Railway

---

## Step 6: Check Frontend Build

The environment variable `NEXT_PUBLIC_API_URL` is embedded at **build time**, not runtime!

**If you just added the variable:**
1. Railway should automatically redeploy
2. Wait for deployment to complete (3-5 minutes)
3. Refresh your browser

**To force redeploy:**
1. Go to **Deployments** tab
2. Click **"Redeploy"** on latest deployment
3. Wait for completion

---

## Quick Diagnostic Checklist

- [ ] Browser console (F12) checked - any errors?
- [ ] Network tab (F12) checked - API calls failing?
- [ ] `NEXT_PUBLIC_API_URL` set in Railway Variables?
- [ ] Backend health check works: `https://web-production-1349.up.railway.app/health`
- [ ] Backend API works: `https://web-production-1349.up.railway.app/api/articles`
- [ ] Frontend redeployed after setting variable?
- [ ] Waited for deployment to complete?

---

## Most Likely Issues

### Issue 1: Environment Variable Not Set (90% likely)
**Fix:** Add `NEXT_PUBLIC_API_URL` in Railway Variables and redeploy

### Issue 2: Backend Not Running
**Fix:** Check backend service status in Railway

### Issue 3: CORS Error
**Fix:** Backend should have CORS enabled (already configured, but verify)

---

## What to Share

Please share:
1. **Browser console errors** (F12 → Console)
2. **Network tab results** (F12 → Network → look for `/api/articles`)
3. **Backend health check result**: Does `https://web-production-1349.up.railway.app/health` work?
4. **Environment variable status**: Is `NEXT_PUBLIC_API_URL` set in Railway?

This will help identify the exact issue!

