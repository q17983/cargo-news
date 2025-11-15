# ✅ Fix: Frontend Not Connecting to Backend

## Current Status
✅ `NEXT_PUBLIC_API_URL` is set correctly  
✅ Backend is healthy  
❌ Frontend still showing "Loading articles..."

## Problem
`NEXT_PUBLIC_API_URL` is embedded at **build time**, not runtime. If you set it after the frontend was built, the frontend is still using the old build without the variable.

## Solution: Force Redeploy

### Step 1: Redeploy Frontend Service

1. **Go to Railway Dashboard**
2. **Click on your Frontend Service**
3. **Go to "Deployments" tab**
4. **Click "Redeploy"** on the latest deployment
5. **Wait for deployment to complete** (3-5 minutes)
6. **Check that deployment shows "Active"** (green checkmark)

### Step 2: Verify Build Includes Variable

After redeploy, check the build logs:
1. **Go to Deployments tab**
2. **Click on the latest deployment**
3. **Check "Logs" tab**
4. **Look for**: The build should complete successfully

### Step 3: Test After Redeploy

1. **Wait for deployment to complete**
2. **Refresh your browser** (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
3. **Check browser console** (F12) for errors
4. **Articles should load** (even if empty array `[]`)

---

## Alternative: Check Browser Console

If redeploy doesn't work, check what's happening:

1. **Press F12** in your browser
2. **Go to "Console" tab**
3. **Look for errors**:
   - `Failed to fetch` → Still can't connect
   - `CORS error` → CORS issue
   - No errors but still loading → API might be slow

4. **Go to "Network" tab**
5. **Refresh page** (F5)
6. **Look for `/api/articles` request**:
   - ✅ **200 OK** → Backend working, just no articles (expected if database is empty)
   - ❌ **Failed** → Connection issue
   - ❌ **CORS error** → CORS configuration issue

---

## Expected Behavior After Fix

### If Database is Empty (Expected):
- Page loads successfully
- Shows "All Sources (0)"
- Shows "0 total tags"
- Shows "Articles (0)" or empty list
- **No "Loading articles..." stuck state**

### Next Steps After Fix:
1. **Go to `/sources` page**
2. **Add news sources**
3. **Click "Scrape All Sources"**
4. **Wait for scraping**
5. **Articles will appear!**

---

## Quick Checklist

- [ ] `NEXT_PUBLIC_API_URL` is set (✅ You have this)
- [ ] Backend is healthy (✅ You have this)
- [ ] Frontend service redeployed after setting variable
- [ ] Deployment shows "Active" status
- [ ] Browser hard refreshed (Ctrl+Shift+R)
- [ ] Browser console checked for errors
- [ ] Network tab checked for API calls

---

## If Still Not Working

Share:
1. **Browser console errors** (F12 → Console)
2. **Network tab results** (F12 → Network → `/api/articles` request)
3. **Deployment logs** (Railway → Deployments → Logs)

This will help identify if it's:
- Build issue (variable not included)
- CORS issue
- API endpoint issue
- Something else

