# 🔑 Update OpenAI API Key - Quick Guide

## ✅ What Was Updated

⚠️ **SECURITY WARNING**: Never commit API keys to Git! Always use environment variables.

## 🚀 Next Steps - Update Railway

### Step 1: Go to Railway Dashboard
1. Navigate to: https://railway.app/dashboard
2. Select your **Backend Service** (Python/FastAPI service)

### Step 2: Update Environment Variable
1. Click on **"Variables"** tab
2. Find `OPENAI_API_KEY` in the list
3. Click on it to edit
4. **Update the value to**: Your actual API key (get it from https://aistudio.google.com/apikey)
5. Click **"Save"**
6. Railway will automatically redeploy the service

### Step 3: Verify
1. Wait for redeployment to complete (2-3 minutes)
2. Check deployment logs for any errors
3. Test scraping to verify API key works

## 📝 Important Notes

- The API key is stored in **Railway environment variables** (NOT in code)
- The key is used by:
  - `app/ai/summarizer.py` - for generating article summaries
  - `scrape_aircargonews.py` - standalone script
  - `scrape_aircargoweek.py` - standalone script
  - `scrape_stattimes.py` - standalone script
  - All scripts get the key from the `OPENAI_API_KEY` environment variable

## ✅ After Update

Once Railway redeploys with the new key:
- All scraping operations will use the new key
- Article summarization will work correctly
- No more "403 API key leaked" errors

## 🐛 If Issues Persist

1. **Check Railway logs** for API key errors
2. **Verify the key** is set correctly in Railway (never commit keys to Git!)
3. **Check for typos** in the Railway variable
4. **Wait 2-3 minutes** after saving for redeployment to complete

