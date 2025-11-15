# 🔧 Fix Port Mismatch Issue

## Problem Identified

Your deployment logs show:
```
- Local:        http://localhost:8080
- Network:      http://0.0.0.0:8080
```

But your Railway domain is configured for **port 3000**!

## Solution: Update Domain Port

### Step 1: Update Domain Port in Railway

1. **Go to Railway Dashboard**
2. **Click on your Frontend Service**
3. **Go to "Settings" tab**
4. **Scroll to "Domains" section**
5. **Find your domain**: `cargo-news-production.up.railway.app`
6. **Click on it** (or the edit/pencil icon)
7. **Change "Target port" from `3000` to `8080`**
8. **Save**

### Step 2: Wait and Test

1. **Wait 30-60 seconds** for the change to propagate
2. **Refresh your browser** at `https://cargo-news-production.up.railway.app`
3. **Website should now load!**

---

## Why This Happened

Railway automatically sets the `PORT` environment variable, and Next.js standalone mode respects it. Railway set it to `8080`, but we configured the domain for `3000`.

---

## Alternative: Force Port 3000

If you prefer to use port 3000, you can:

1. **Go to Frontend Service → Variables tab**
2. **Add or update**:
   ```
   PORT = 3000
   ```
3. **Redeploy** the service
4. **Keep domain on port 3000**

But the easier solution is to just update the domain to port 8080 (what Railway is actually using).

---

## ✅ Quick Fix Summary

1. **Settings → Domains → Edit domain**
2. **Change port from 3000 to 8080**
3. **Save**
4. **Wait 30 seconds**
5. **Refresh browser**

That's it! Your website should work now.

