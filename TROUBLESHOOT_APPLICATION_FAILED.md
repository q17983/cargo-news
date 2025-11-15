# 🔧 Troubleshoot "Application failed to respond"

## Problem
Domain is generated but application isn't responding.

## Step 1: Check Deployment Logs

1. **Go to Railway Dashboard**
2. **Click on your Frontend Service**
3. **Go to "Deployments" tab**
4. **Click on the latest deployment**
5. **Check "Logs" tab**

### What to Look For:

**✅ Good Signs:**
- "Starting Container"
- "Server running on port 3000"
- No error messages
- Deployment shows "Active" (green checkmark)

**❌ Bad Signs:**
- "sh: next: not found" (wrong start command)
- "Cannot find module" errors
- "Port already in use" errors
- Deployment shows "Failed" (red X)

---

## Step 2: Verify Start Command

### Check Railway Settings:

1. **Go to Frontend Service → Settings tab**
2. **Check "Start Command"** (if visible)
3. **Should be**: `node server.js` (NOT `npm start` or `next start`)

### Check railway.json:

The file should have:
```json
{
  "deploy": {
    "startCommand": "node server.js"
  }
}
```

---

## Step 3: Check Environment Variables

1. **Go to Frontend Service → Variables tab**
2. **Verify you have**:
   ```
   NEXT_PUBLIC_API_URL = https://web-production-1349.up.railway.app
   ```
   (No trailing slash!)

---

## Step 4: Common Issues & Fixes

### Issue 1: Wrong Start Command

**Error in logs:** `sh: next: not found`

**Fix:**
1. Go to **Settings → Variables**
2. Add or update:
   ```
   RAILWAY_START_COMMAND = node server.js
   ```
3. Or update `railway.json` (already done, but verify it's in Git)

### Issue 2: Build Failed

**Error in logs:** Build errors during `npm run build`

**Fix:**
- Check build logs for specific errors
- Common: Missing files, import errors
- Redeploy after fixing

### Issue 3: Port Mismatch

**Error:** Application not listening on port 3000

**Fix:**
- Verify Dockerfile has `ENV PORT 3000`
- Verify Railway domain is set to port 3000
- Check logs for "listening on port" message

### Issue 4: Missing Files

**Error:** `Cannot find module` or file not found

**Fix:**
- Verify all files are in Git
- Check that `lib/api.ts` exists
- Verify `public/` directory exists

---

## Step 5: Force Redeploy

If nothing else works:

1. **Go to Deployments tab**
2. **Click "Redeploy"** on the latest deployment
3. **Wait for build to complete** (3-5 minutes)
4. **Check logs again**

---

## Step 6: Verify Build Succeeded

1. **Go to Deployments tab**
2. **Latest deployment should show**:
   - ✅ "Active" status (green)
   - Build completed successfully
   - No error messages

---

## Quick Diagnostic Checklist

- [ ] Latest deployment shows "Active" (not "Failed")
- [ ] Logs show "Starting Container" and no errors
- [ ] Start command is `node server.js` (not `next start`)
- [ ] `NEXT_PUBLIC_API_URL` is set correctly
- [ ] Build completed successfully
- [ ] Port 3000 is configured in domain settings
- [ ] All files are in Git (especially `lib/api.ts`)

---

## What to Share for Help

If still not working, share:

1. **Latest deployment logs** (from Deployments → Logs)
2. **Deployment status** (Active/Failed)
3. **Any error messages** you see
4. **Start command** from Settings or railway.json

---

## Expected Log Output (When Working)

```
Starting Container
> cargo-news-frontend@1.0.0 start
> node server.js
Server running on port 3000
```

If you see this, the app is running and the issue might be:
- Network configuration
- Domain not fully propagated (wait 1-2 minutes)
- Backend connection issue

