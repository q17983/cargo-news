# 🔧 Fix Root Directory Setting

## ❌ Current Setting (WRONG)
```
Root Directory: /frontend
```

## ✅ Correct Setting
```
Root Directory: frontend
```

## 📋 How to Fix

1. **In Railway Dashboard**
   - Go to your **frontend service**
   - Click **"Settings"** tab
   - Find **"Root Directory"** field

2. **Change the Value**
   - **Remove the leading slash** `/`
   - Change from: `/frontend`
   - Change to: `frontend`
   - Click **"Save"**

3. **Redeploy**
   - Go to **"Deployments"** tab
   - Click **"Redeploy"**
   - Wait for new build

---

## 💡 Why This Matters

- `/frontend` (with slash) = Absolute path from root filesystem (wrong)
- `frontend` (no slash) = Relative path from repository root (correct)

Railway needs the relative path `frontend` to correctly find your frontend code in the repository.

---

## ✅ After Fixing

Once you change it to `frontend` (no slash) and redeploy:
- Railway will build from `frontend/` directory
- Will find `package.json` correctly
- Will resolve `@/lib/api` imports
- Build will succeed!

