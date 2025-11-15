# 🔧 Fix: Frontend Calling localhost Instead of Production API

## Problem

Frontend is trying to fetch from:
- ❌ `http://localhost:8000/api/sources`
- ✅ Should be: `https://web-production-1349.up.railway.app/api/sources`

**Console Errors:**
- `[blocked] The page at https://cargo-news-production.up.railway.app/sources was not allowed to display insecure content from http://localhost:8000/api/sources`
- `Fetch API cannot load http://localhost:8000/api/sources due to access control checks`

## Root Cause

The `NEXT_PUBLIC_API_URL` environment variable is either:
1. **Not set** in Railway frontend service
2. **Set incorrectly** (wrong value)
3. **Frontend was built before** the env var was set (Next.js embeds env vars at build time)

## Solution

### Step 1: Check Railway Environment Variables

1. Go to **Railway Dashboard**
2. Select **Frontend Service** (the one serving `cargo-news-production.up.railway.app`)
3. Click **Variables** tab
4. Look for `NEXT_PUBLIC_API_URL`

### Step 2: Add/Update Environment Variable

**If `NEXT_PUBLIC_API_URL` is missing or wrong:**

1. Click **"+ New Variable"** button (or edit existing)
2. **Name:** `NEXT_PUBLIC_API_URL`
3. **Value:** `https://web-production-1349.up.railway.app`
4. Click **Save**

**⚠️ Important:** 
- Do NOT include trailing slash: `https://web-production-1349.up.railway.app` ✅
- NOT: `https://web-production-1349.up.railway.app/` ❌

### Step 3: Wait for Redeploy

1. Railway will **automatically redeploy** the frontend after saving
2. Wait **2-3 minutes** for deployment to complete
3. Check Railway **Deployments** tab to see progress

### Step 4: Hard Refresh Browser

After deployment completes:

1. **Hard refresh** the page:
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`
2. Or **clear cache** and reload

### Step 5: Verify Fix

1. Open **Browser Console** (F12)
2. Check for errors - should be **no more localhost errors**
3. Page should load articles and sources

---

## Verification

After fixing, test in browser console:

```javascript
// Should work now
fetch('https://web-production-1349.up.railway.app/api/sources')
  .then(r => r.json())
  .then(data => console.log('✅ Sources:', data))
  .catch(err => console.error('❌ Error:', err));
```

---

## Why This Happens

**Next.js Environment Variables:**
- Variables starting with `NEXT_PUBLIC_` are embedded at **build time**
- If the variable is set **after** the build, the old value (or default) is still used
- **Solution:** Set the variable **before** building, or trigger a new build after setting it

**Railway Auto-Redeploy:**
- When you save an environment variable, Railway automatically triggers a new build
- This ensures the new value is embedded in the build

---

## Quick Checklist

- [ ] Go to Railway → Frontend Service → Variables
- [ ] Check if `NEXT_PUBLIC_API_URL` exists
- [ ] Set/Update to: `https://web-production-1349.up.railway.app`
- [ ] Save (wait for auto-redeploy)
- [ ] Wait 2-3 minutes
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Verify no more localhost errors in console
- [ ] Page should load successfully

---

## Still Not Working?

If after setting the variable and redeploying it still doesn't work:

1. **Check Railway Build Logs:**
   - Frontend service → Deployments → Latest deployment → View logs
   - Look for any build errors

2. **Verify Variable Name:**
   - Must be exactly: `NEXT_PUBLIC_API_URL`
   - Case-sensitive!

3. **Check Variable Value:**
   - No trailing slash
   - No quotes around the value
   - Should be: `https://web-production-1349.up.railway.app`

4. **Force Redeploy:**
   - Settings → Redeploy
   - This forces a fresh build with the new env var

