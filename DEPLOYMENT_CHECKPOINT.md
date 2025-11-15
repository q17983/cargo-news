# ✅ Deployment Checkpoint - Working Configuration

**Date:** 2025-11-15  
**Status:** ✅ Frontend and Backend Successfully Deployed on Railway  
**Frontend URL:** `https://cargo-news-production.up.railway.app`  
**Backend URL:** `https://web-production-1349.up.railway.app`

---

## 🎯 Critical Configuration Summary

### Frontend Environment Variables (Railway)

**Service:** `cargo-news` (Frontend)

| Variable Name | Value | Required |
|--------------|-------|----------|
| `NEXT_PUBLIC_API_URL` | `https://web-production-1349.up.railway.app` | ✅ **CRITICAL** |

**⚠️ Important:**
- Must be set BEFORE building
- No trailing slash
- No quotes around value
- Must be HTTPS (not HTTP)

### Backend Environment Variables (Railway)

**Service:** `web` (Backend)

| Variable Name | Purpose | Required |
|--------------|---------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_KEY` | Supabase anon key | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `SCRAPING_DELAY_SECONDS` | Delay between requests | Optional |
| `MAX_RETRIES` | Max retry attempts | Optional |
| `PORT` | Server port (Railway sets automatically) | Auto |

---

## 🔧 Key Files Configuration

### 1. Frontend Dockerfile (`frontend/Dockerfile`)

**CRITICAL:** Must explicitly pass `NEXT_PUBLIC_API_URL` during build:

```dockerfile
# In builder stage, BEFORE npm run build:
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Verify it's set
RUN echo "=== Checking NEXT_PUBLIC_API_URL ===" && \
    if [ -z "$NEXT_PUBLIC_API_URL" ]; then \
      echo "❌ WARNING: NEXT_PUBLIC_API_URL is not set!"; \
    else \
      echo "✅ NEXT_PUBLIC_API_URL is set to: $NEXT_PUBLIC_API_URL"; \
    fi

# Then build
RUN npm run build
```

**Why:** Next.js embeds `NEXT_PUBLIC_*` variables at build time. Without this, it defaults to `http://localhost:8000`.

### 2. Frontend API Client (`frontend/lib/api.ts`)

**Current Configuration:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug logging (always enabled)
if (typeof window !== 'undefined') {
  console.log('🔍 API_URL being used:', API_URL);
  if (API_URL.includes('localhost')) {
    console.error('❌ WARNING: Using localhost! NEXT_PUBLIC_API_URL was not set during build!');
  }
}
```

### 3. Frontend Railway Config (`frontend/railway.json`)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "node server.js"
  }
}
```

**Root Directory:** Must be set to `frontend` (no leading slash) in Railway settings.

### 4. Backend Configuration (`app/config.py`)

Uses `pydantic-settings` to load from environment variables:
- All sensitive keys loaded from Railway environment variables
- No hardcoded values

---

## 📋 Deployment Checklist

### Initial Setup

- [ ] **Supabase Setup**
  - [ ] Database tables created (`database_schema.sql`)
  - [ ] RLS policies enabled (allow all for single-user app)
  - [ ] Bookmarks table created (`add_bookmarks_table.sql`)
  - [ ] Full-text search enabled for articles

- [ ] **Railway Services Created**
  - [ ] Backend service (`web`)
  - [ ] Frontend service (`cargo-news`)

- [ ] **Environment Variables Set**
  - [ ] Backend: `SUPABASE_URL`, `SUPABASE_KEY`, `GEMINI_API_KEY`
  - [ ] Frontend: `NEXT_PUBLIC_API_URL` (MUST be set before first build)

### Deployment Steps

#### Backend Deployment

1. [ ] Push code to GitHub (Railway auto-deploys)
2. [ ] Verify environment variables are set
3. [ ] Check build logs for errors
4. [ ] Verify service is running: `https://web-production-1349.up.railway.app/health`
5. [ ] Test API: `curl https://web-production-1349.up.railway.app/api/articles?limit=5`

#### Frontend Deployment

1. [ ] **CRITICAL:** Set `NEXT_PUBLIC_API_URL` in Railway Variables FIRST
2. [ ] Push code to GitHub (Railway auto-deploys)
3. [ ] Check build logs for:
   - `✅ NEXT_PUBLIC_API_URL is set to: https://web-production-1349.up.railway.app`
   - If shows `❌ WARNING: NEXT_PUBLIC_API_URL is not set!` → Fix immediately
4. [ ] Wait for build to complete
5. [ ] Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
6. [ ] Check browser console:
   - Should show: `🔍 API_URL being used: https://web-production-1349.up.railway.app`
   - Should show: `✅ Using production API URL`
   - Should NOT show: `❌ WARNING: Using localhost!`

### Post-Deployment Verification

- [ ] Frontend loads without errors
- [ ] No `localhost:8000` errors in console
- [ ] API calls go to production backend
- [ ] Articles load successfully
- [ ] Sources page works
- [ ] Scraping functionality works

---

## 🚨 Common Mistakes & How to Avoid

### Mistake 1: Frontend Using localhost:8000

**Symptom:** Console shows `Fetch API cannot load http://localhost:8000/api/...`

**Causes:**
1. `NEXT_PUBLIC_API_URL` not set in Railway
2. Variable set AFTER first build (Next.js embeds at build time)
3. Dockerfile not passing variable during build

**Solution:**
1. Set `NEXT_PUBLIC_API_URL` in Railway Variables
2. Ensure Dockerfile has `ARG NEXT_PUBLIC_API_URL` and `ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL` BEFORE `npm run build`
3. Force redeploy to rebuild with new variable
4. Check build logs to verify variable is set

### Mistake 2: Build Fails with Module Not Found

**Symptom:** `Module not found: Can't resolve '@/lib/api'`

**Causes:**
1. Root Directory not set correctly in Railway
2. Path aliases not configured in `tsconfig.json`
3. Files not tracked in Git

**Solution:**
1. Set Root Directory to `frontend` (no leading slash) in Railway
2. Use relative imports instead of `@/` aliases
3. Ensure `frontend/lib/api.ts` is tracked in Git (check `.gitignore`)

### Mistake 3: Port Mismatch

**Symptom:** "Application failed to respond" after generating domain

**Causes:**
1. Frontend running on different port than Railway expects
2. Target port in Railway domain settings is wrong

**Solution:**
1. Check what port frontend is running on (check deploy logs)
2. Set Target Port in Railway domain settings to match
3. For Next.js standalone, usually port 3000 or 8080

### Mistake 4: Environment Variables Not Available During Build

**Symptom:** Build log shows `❌ WARNING: NEXT_PUBLIC_API_URL is not set!`

**Causes:**
1. Variable not set in Railway
2. Railway not passing variables to Docker build
3. Variable name typo

**Solution:**
1. Verify variable exists in Railway Variables tab
2. Check variable name is exactly `NEXT_PUBLIC_API_URL` (case-sensitive)
3. Ensure Dockerfile has `ARG NEXT_PUBLIC_API_URL` before build step
4. Check Railway build logs to see if variable is available

### Mistake 5: API Key Leaked/Invalid

**Symptom:** `403 Your API key was reported as leaked`

**Causes:**
1. Old API key still in Railway environment variables
2. API key exposed in code (should never happen)

**Solution:**
1. Generate new API key from Google AI Studio
2. Update `GEMINI_API_KEY` in Railway backend service Variables
3. Railway will auto-redeploy
4. Never commit API keys to Git

---

## 🔍 Troubleshooting Guide

### Frontend Stuck at Loading

1. **Check Browser Console:**
   - Look for errors (red messages)
   - Check if API calls are going to correct domain
   - Verify no `localhost:8000` errors

2. **Check Network Tab:**
   - See which requests are failing
   - Check request URLs (should be production backend)
   - Check response status codes

3. **Check Railway Build Logs:**
   - Verify `NEXT_PUBLIC_API_URL` was set during build
   - Look for build errors

4. **Verify Environment Variable:**
   - Railway → Frontend Service → Variables
   - Check `NEXT_PUBLIC_API_URL` exists and is correct

### Backend Not Responding

1. **Check Health Endpoint:**
   ```bash
   curl https://web-production-1349.up.railway.app/health
   ```
   Should return: `{"status":"healthy"}`

2. **Check Railway Logs:**
   - Backend service → Deployments → Latest → View Logs
   - Look for errors or startup issues

3. **Verify Environment Variables:**
   - Check all required variables are set
   - Verify Supabase credentials are correct
   - Verify Gemini API key is valid

### Scraping Not Working

1. **Check Running Tasks:**
   ```bash
   curl https://web-production-1349.up.railway.app/api/scrape/running
   ```

2. **Check Scraping Logs:**
   - Railway backend logs
   - Supabase `scraping_logs` table

3. **Verify API Keys:**
   - Gemini API key is valid and not exceeded quota
   - Supabase credentials are correct

---

## 📝 Development vs Production

### Local Development

**Frontend:**
- Runs on `http://localhost:3000`
- Uses `NEXT_PUBLIC_API_URL` from `.env.local` (defaults to `http://localhost:8000`)
- Hot reload enabled

**Backend:**
- Runs on `http://localhost:8000`
- Uses `.env` file for environment variables
- Can run scrapers directly: `python scrape_aircargoweek.py`

### Production (Railway)

**Frontend:**
- Runs on Railway domain (e.g., `cargo-news-production.up.railway.app`)
- Uses `NEXT_PUBLIC_API_URL` from Railway Variables (embedded at build time)
- Standalone build (no hot reload)

**Backend:**
- Runs on Railway domain (e.g., `web-production-1349.up.railway.app`)
- Uses environment variables from Railway
- Scrapers run via API endpoints or scheduled jobs

---

## 🔐 Security Best Practices

1. **Never commit API keys or secrets to Git**
   - Use `.gitignore` for `.env` files
   - Use Railway environment variables for production

2. **Use different API keys for dev/prod**
   - Local development: `.env` file
   - Production: Railway environment variables

3. **Rotate API keys if exposed**
   - If key is leaked, generate new one immediately
   - Update in Railway Variables
   - Old key will stop working

4. **Check for hardcoded values**
   - Search codebase for API keys
   - Use environment variables everywhere

---

## 📚 Key Lessons Learned

1. **Next.js Environment Variables:**
   - `NEXT_PUBLIC_*` variables are embedded at BUILD TIME
   - Must be set BEFORE building
   - Cannot be changed at runtime
   - Must explicitly pass to Docker build with `ARG` and `ENV`

2. **Railway Deployment:**
   - Environment variables must be set in Railway UI
   - Docker builds need explicit `ARG` to receive variables
   - Root Directory must be set correctly for monorepos
   - Auto-deploys on git push (if connected to GitHub)

3. **Debugging:**
   - Always check browser console first
   - Check Network tab for failed requests
   - Check Railway build logs for build-time issues
   - Add logging to verify configuration

4. **Testing:**
   - Test API endpoints directly with `curl`
   - Verify environment variables are set correctly
   - Check build logs for warnings
   - Test in browser after deployment

---

## 🎯 Quick Reference

### Railway Services

| Service | Purpose | Domain |
|---------|---------|--------|
| `web` | Backend API | `web-production-1349.up.railway.app` |
| `cargo-news` | Frontend | `cargo-news-production.up.railway.app` |

### Critical Environment Variables

**Frontend:**
- `NEXT_PUBLIC_API_URL` = `https://web-production-1349.up.railway.app`

**Backend:**
- `SUPABASE_URL` = (from Supabase dashboard)
- `SUPABASE_KEY` = (from Supabase dashboard)
- `GEMINI_API_KEY` = (from Google AI Studio)

### Important URLs

- **Frontend:** https://cargo-news-production.up.railway.app
- **Backend Health:** https://web-production-1349.up.railway.app/health
- **Backend API:** https://web-production-1349.up.railway.app/api

---

## ✅ Deployment Success Criteria

- [ ] Frontend loads without errors
- [ ] No `localhost:8000` in browser console
- [ ] API calls go to production backend
- [ ] Articles load and display correctly
- [ ] Sources page works
- [ ] Scraping functionality works
- [ ] Bookmarks work
- [ ] All API endpoints respond correctly

---

**Last Updated:** 2025-11-15  
**Status:** ✅ Production Deployment Working

