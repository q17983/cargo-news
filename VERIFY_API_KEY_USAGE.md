# ✅ Verify API Key Usage

## Current Status
All scripts correctly use environment variables - **NO hardcoded keys found!**

## How API Key is Loaded

### 1. Backend (FastAPI)
- **File**: `app/config.py`
- **Loads**: `openai_api_key: str` from environment variable `OPENAI_API_KEY`
- **Used by**: `app/ai/summarizer.py` via `settings.openai_api_key`

### 2. Standalone Scripts
- **Files**: `scrape_aircargoweek.py`, `scrape_aircargonews.py`, `scrape_stattimes.py`
- **All import**: `from app.ai.summarizer import Summarizer`
- **Summarizer uses**: `settings.openai_api_key` (from environment variable)

### 3. Subprocess (Air Cargo Week)
- **Runs**: `scrape_aircargoweek.py` as subprocess
- **Uses**: Environment variables from Railway
- **No hardcoded keys**

---

## ✅ Verification: All Scripts Use Environment Variable

✅ `app/ai/summarizer.py` → Uses `settings.openai_api_key`  
✅ `app/config.py` → Loads from `OPENAI_API_KEY` env var  
✅ `scrape_aircargoweek.py` → Uses Summarizer (env var)  
✅ `scrape_aircargonews.py` → Uses Summarizer (env var)  
✅ `scrape_stattimes.py` → Uses Summarizer (env var)  
✅ Backend API routes → Use Summarizer (env var)  

**No hardcoded API keys found!**

---

## 🔧 Fix: Update API Key in Railway

The error "403 Your API key was reported as leaked" means:
1. The API key in Railway might be the old/leaked one
2. OR the new key needs to be set in Railway

### Step 1: Update API Key in Railway

1. **Go to Railway Dashboard**
2. **Click on Backend Service** (not frontend)
3. **Go to "Variables" tab**
4. **Find `OPENAI_API_KEY`**
5. **Click to edit**
6. **Update value to**: Your actual API key (get it from https://aistudio.google.com/apikey)
7. **Click "Save"**
8. **Railway will automatically redeploy** the backend

### Step 2: Verify After Redeploy

1. **Wait for redeployment** (2-3 minutes)
2. **Check backend logs** for any API key errors
3. **Try scraping again** from the website
4. **Should work now!**

---

## Why This Happened

The API key error suggests:
- The old API key was leaked/compromised
- Google detected it and blocked it
- The new key needs to be set in Railway (never commit keys to Git!)

---

## Quick Checklist

- [ ] `OPENAI_API_KEY` is set in Railway Backend Variables
- [ ] Value is set correctly (never commit actual keys to Git!)
- [ ] Backend service redeployed after updating
- [ ] No API key errors in backend logs
- [ ] Scraping works for Air Cargo News and STAT Times (already working)
- [ ] Scraping works for Air Cargo Week (should work after key update)

---

## Important Notes

1. **All scripts use environment variables** - no code changes needed
2. **Just update the Railway variable** and redeploy
3. **The new key should work** (you confirmed it works for other sources)
4. **After updating, Air Cargo Week should work too**

Update the `OPENAI_API_KEY` in Railway Backend Variables and redeploy!

