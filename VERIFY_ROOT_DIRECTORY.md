# ⚠️ CRITICAL: Verify Root Directory Setting

## The Problem

Railway is still building from the **root directory** instead of `frontend/`, which is why `@/lib/api` can't be found.

## ✅ Solution: Double-Check Root Directory

### Step 1: Go to Frontend Service

1. In Railway Dashboard
2. Click on your **FRONTEND service** (not backend)
3. Make sure you're looking at the frontend service

### Step 2: Check Settings

1. Click **"Settings"** tab
2. Scroll down to find **"Root Directory"** field
3. **It MUST say**: `frontend`
4. If it says anything else (like `/` or empty), change it to: `frontend`
5. Click **"Save"**

### Step 3: Verify It's Saved

1. Refresh the page
2. Go back to Settings
3. Confirm Root Directory still says `frontend`

### Step 4: Force Redeploy

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** button
3. Wait for new build

---

## 🔍 How to Verify Root Directory is Set

**In Railway Settings, you should see:**

```
Root Directory: frontend
```

**NOT:**
```
Root Directory: /
```
or
```
Root Directory: (empty)
```

---

## 🆘 If Root Directory Setting Doesn't Exist

If you don't see a "Root Directory" field in Settings:

1. **Check if you're in the right service** (frontend, not backend)
2. **Try a different browser** or clear cache
3. **Contact Railway support** - Root Directory should be available

---

## 📸 Visual Guide

**Correct Settings View:**
```
┌─────────────────────────────┐
│ Settings                    │
├─────────────────────────────┤
│ Service Name: frontend       │
│                             │
│ Root Directory: frontend    │ ← Must say "frontend"
│                             │
│ [Save]                      │
└─────────────────────────────┘
```

---

## ✅ After Setting Root Directory

Railway will:
- Build from `frontend/` directory
- Find `package.json` in `frontend/`
- Resolve `@/lib/api` correctly
- Build successfully

---

## 💡 Alternative: Delete and Recreate Service

If Root Directory setting doesn't work:

1. **Delete the frontend service** in Railway
2. **Create a new service** from GitHub repo
3. **Immediately set Root Directory to `frontend`** before first build
4. **Set environment variable**: `NEXT_PUBLIC_API_URL`
5. **Deploy**

This ensures the service is created with the correct root directory from the start.

