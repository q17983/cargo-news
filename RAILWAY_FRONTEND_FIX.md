# 🔧 Fix Frontend Build Issue on Railway

## Problem
Railway is building from the root directory instead of `frontend/`, causing `@/lib/api` imports to fail.

## Solution: Set Root Directory in Railway

### Step 1: Verify Root Directory Setting

1. **Go to Railway Dashboard**
2. **Click on your frontend service** (not the backend)
3. **Go to "Settings" tab**
4. **Find "Root Directory" field**
5. **Make sure it's set to**: `frontend`
6. **Click "Save"**

### Step 2: Verify Environment Variable

1. **Go to "Variables" tab**
2. **Make sure you have**:
   ```
   NEXT_PUBLIC_API_URL = https://web-production-1349.up.railway.app
   ```

### Step 3: Trigger Redeploy

After setting Root Directory:
1. Railway should automatically redeploy
2. OR go to "Deployments" tab → Click "Redeploy"

---

## Alternative: If Root Directory Setting Doesn't Work

If Railway still builds from root, we can add a `railway.json` in the frontend directory:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm install && npm run build"
  },
  "deploy": {
    "startCommand": "npm start"
  }
}
```

But first, try setting the Root Directory in Railway settings - that's the proper solution.

---

## What to Check

✅ Root Directory = `frontend`  
✅ NEXT_PUBLIC_API_URL = `https://web-production-1349.up.railway.app`  
✅ Service is redeployed after changes

