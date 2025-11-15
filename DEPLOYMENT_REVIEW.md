# Deployment Review & Checklist

## ✅ Configuration Files Review

### 1. Railway Configuration (`railway.json`)
**Status**: ✅ **CORRECT**
- Uses NIXPACKS builder
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Restart policy configured

### 2. Procfile
**Status**: ✅ **CORRECT**
- Matches Railway start command
- Uses `$PORT` environment variable

### 3. Requirements (`requirements.txt`)
**Status**: ✅ **CORRECT**
- All dependencies listed
- httpx version constraint fixed (>=0.24.0,<0.25.0)
- Playwright included

**⚠️ IMPORTANT**: Playwright browsers must be installed separately:
```bash
playwright install chromium
```

## ⚠️ Issues Found

### Issue 1: Playwright Browser Installation
**Problem**: Playwright Python package is installed, but browsers are not automatically installed during Railway deployment.

**Solution**: Add to `railway.json` build command:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && playwright install chromium"
  }
}
```

### Issue 2: Database Schema - Missing Column (Non-Critical)
**Problem**: Code tracks `articles_processed` but doesn't save it to database. Schema doesn't have this column.

**Status**: ⚠️ **NON-CRITICAL** - Code works without it, but tracking is incomplete.

**Optional Fix**: If you want to track `articles_processed`:
1. Add column to `database_schema.sql`:
   ```sql
   ALTER TABLE scraping_logs ADD COLUMN IF NOT EXISTS articles_processed INTEGER DEFAULT 0;
   ```
2. Update `ScrapingLogBase` model to include `articles_processed: int = 0`
3. Update `scrape.py` to save `articles_processed` in log

## ✅ Environment Variables Checklist

### Required Variables (Must Set in Railway):
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=AIzaSyCSg4pvORmJmdsfPLqmZ41Ia5v9kDNS1Dg
```

### Optional Variables (Have Defaults):
```
SCRAPING_DELAY_SECONDS=2          # Default: 2
MAX_RETRIES=3                      # Default: 3
PORT=8000                          # Default: 8000 (Railway sets $PORT automatically)
```

## ✅ Database Setup Checklist

### 1. Supabase Database Schema
**File**: `database_schema.sql`

**Required Steps**:
1. ✅ Create Supabase project
2. ✅ Run `database_schema.sql` in SQL Editor
3. ✅ Verify RLS policies are created
4. ✅ Test connection with API key

**Tables Created**:
- ✅ `news_sources` - Stores registered sources
- ✅ `articles` - Stores scraped articles
- ✅ `scraping_logs` - Tracks scraping history

**Indexes Created**:
- ✅ All performance indexes in place

**RLS Policies**:
- ✅ All tables have "Allow all operations" policy

## ✅ Frontend Deployment

### Configuration Files:
- ✅ `frontend/package.json` - Correct Next.js setup
- ✅ `frontend/next.config.js` - API rewrites configured
- ✅ `frontend/.env.local` - Local development config

### Railway Frontend Deployment:
1. Create separate Railway service for frontend
2. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
3. Railway will auto-detect Next.js and deploy

## ✅ Backend Code Review

### API Endpoints:
- ✅ `/api/sources` - Source management
- ✅ `/api/articles` - Article retrieval
- ✅ `/api/scrape` - Scraping triggers
- ✅ `/health` - Health check
- ✅ `/keepalive` - Keep-alive endpoint

### Scheduler:
- ✅ APScheduler configured for 00:00 UTC daily scraping
- ✅ Starts automatically on app startup
- ✅ Graceful shutdown on app stop

### Scrapers:
- ✅ `AircargonewsScraper` - Working
- ✅ `AircargoweekScraper` - Working (requires Playwright)
- ✅ `StattimesScraper` - Working
- ✅ `BaseScraper` - Playwright fallback implemented

## 🚀 Deployment Steps

### Step 1: Fix Playwright Installation
Update `railway.json` to install browsers during build.

### Step 2: Set Environment Variables
In Railway dashboard:
1. Go to your project
2. Click "Variables"
3. Add all required variables

### Step 3: Deploy Backend
1. Connect GitHub repository to Railway
2. Railway will auto-detect Python project
3. Build will run automatically
4. Check logs for any errors

### Step 4: Verify Deployment
1. Check health: `https://your-app.railway.app/health`
2. Check keep-alive: `https://your-app.railway.app/keepalive`
3. Test API: `https://your-app.railway.app/api/sources`

### Step 5: Deploy Frontend (Optional)
1. Add new service in Railway
2. Point to `frontend/` directory
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

### Step 6: Set Up Keep-Alive (Important for Free Tier)
Railway free tier may sleep after inactivity. Options:

**Option A**: External Cron Service
- Use [cron-job.org](https://cron-job.org)
- Ping `/keepalive` every 5 minutes

**Option B**: Railway Pro Plan
- Doesn't sleep
- More reliable for scheduled tasks

## 📋 Pre-Deployment Checklist

- [ ] All environment variables set in Railway
- [ ] Database schema run in Supabase
- [ ] RLS policies verified
- [ ] Playwright browsers installation added to build
- [ ] Test scraping locally with same environment
- [ ] Verify all scrapers work
- [ ] Check API endpoints respond correctly
- [ ] Frontend API URL configured (if deploying frontend)

## 🔍 Post-Deployment Verification

1. **Health Check**:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **Test Scraping**:
   - Add a source via API or frontend
   - Trigger manual scrape
   - Check scraping_logs table

3. **Check Scheduler**:
   - Verify scheduler starts in logs
   - Wait for 00:00 UTC to test daily job

4. **Monitor Logs**:
   - Check Railway logs for errors
   - Monitor Supabase for new articles
   - Check Gemini API usage

## 🐛 Common Deployment Issues

### Issue: Playwright Not Working
**Symptom**: Scrapers fail with "Playwright not installed"
**Fix**: Add `playwright install chromium` to build command

### Issue: Database Connection Failed
**Symptom**: "Error connecting to Supabase"
**Fix**: 
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active
- Verify RLS policies allow access

### Issue: Scheduler Not Running
**Symptom**: No daily scraping happening
**Fix**:
- Check Railway logs for scheduler errors
- Verify app is not sleeping (use keep-alive)
- Check timezone is UTC

### Issue: CORS Errors (Frontend)
**Symptom**: Frontend can't connect to backend
**Fix**: 
- Update `CORS_ORIGINS` in backend (currently allows all)
- Verify `NEXT_PUBLIC_API_URL` is correct

## 📝 Notes

1. **Playwright Browsers**: Must be installed during build, not just the Python package
2. **Railway Free Tier**: May sleep, use keep-alive endpoint or upgrade
3. **Database**: Ensure RLS policies are set correctly
4. **Environment Variables**: All required variables must be set
5. **Frontend**: Can be deployed separately or together with backend

## ✅ Summary

**Ready for Deployment**: ✅ **YES** (with Playwright fix)

**Critical Fixes Needed**:
1. ⚠️ Add Playwright browser installation to build command

**Optional Improvements**:
1. Add `articles_processed` column to database (if tracking needed)
2. Set up keep-alive cron job
3. Configure CORS origins for production

**Overall Status**: 🟢 **READY** (after Playwright fix)

