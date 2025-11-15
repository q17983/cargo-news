# 🔧 Complete Fix for Frontend Build Issue

## Current Problem
Railway build fails with: `Module not found: Can't resolve '@/lib/api'`

## Root Cause
Railway is building from the wrong directory OR the Root Directory setting has a leading slash.

---

## ✅ Solution 1: Fix Root Directory (MOST IMPORTANT)

### Step 1: Verify Root Directory Setting

1. **Go to Railway Dashboard**
2. **Click on your FRONTEND service** (not backend)
3. **Go to "Settings" tab**
4. **Find "Root Directory" field**

### Step 2: Check Current Value

**❌ WRONG:**
```
Root Directory: /frontend
```

**✅ CORRECT:**
```
Root Directory: frontend
```

### Step 3: Fix It

1. **Change from**: `/frontend` (with leading slash)
2. **Change to**: `frontend` (NO leading slash)
3. **Click "Save"**
4. **Go to Deployments tab**
5. **Click "Redeploy"**

---

## ✅ Solution 2: Verify Environment Variable

1. **Go to "Variables" tab** in frontend service
2. **Make sure you have**:
   ```
   NEXT_PUBLIC_API_URL = https://web-production-1349.up.railway.app
   ```
3. **No trailing slash** in the URL!

---

## ✅ Solution 3: What We've Already Fixed

1. ✅ Added `baseUrl: "."` to `tsconfig.json`
2. ✅ Added webpack alias to `next.config.js`
3. ✅ Created `frontend/railway.json`

All pushed to GitHub.

---

## 🧪 Test Locally First

Before deploying, test the build locally:

```bash
cd "/Users/sai/Cargo News/frontend"
npm run build
```

If this works locally, the issue is definitely the Root Directory setting in Railway.

---

## 🔄 Complete Redeploy Process

1. **Fix Root Directory** to `frontend` (no slash)
2. **Verify Environment Variable** is set
3. **Save Settings**
4. **Go to Deployments**
5. **Click "Redeploy"**
6. **Wait for build** (3-5 minutes)
7. **Check logs** for success

---

## 🆘 If Still Failing

### Option A: Delete and Recreate Service

1. **Delete the frontend service** in Railway
2. **Create new service** from GitHub repo
3. **IMMEDIATELY set Root Directory to `frontend`** (before first build)
4. **Set environment variable**: `NEXT_PUBLIC_API_URL`
5. **Deploy**

### Option B: Check Build Logs

Look for these in the logs:
- `COPY . /app/.` - Should copy from `frontend/` directory
- `npm ci` - Should run in `frontend/` directory
- `npm run build` - Should find `package.json` in current directory

If logs show it's copying from root or running commands in wrong directory, Root Directory is wrong.

---

## ✅ Success Indicators

When it works, you'll see in logs:
- ✅ `Creating an optimized production build ...`
- ✅ `Compiled successfully`
- ✅ `Route (app)`
- ✅ `Build completed`

---

## 📝 Checklist

- [ ] Root Directory = `frontend` (no leading slash)
- [ ] NEXT_PUBLIC_API_URL = `https://web-production-1349.up.railway.app` (no trailing slash)
- [ ] Settings saved
- [ ] Service redeployed
- [ ] Build logs show success

---

## 💡 Key Point

**The Root Directory MUST be `frontend` (relative path, no slash).**

If it's `/frontend` (absolute path with slash), Railway looks in the wrong place and can't find your files!

