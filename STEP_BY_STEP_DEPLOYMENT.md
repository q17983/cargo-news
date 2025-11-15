# 🚀 Step-by-Step Railway Deployment Guide

Follow these exact steps to deploy your system to Railway.

---

## 📋 Prerequisites Checklist

✅ Railway account (you have it!)  
✅ GitHub account (you have it!)  
✅ Code ready in a GitHub repository  
✅ Supabase project set up  
✅ Google Gemini API key  

---

## 🔧 Step 1: Prepare Your Code for GitHub

### 1.1 Check if Code is Already on GitHub

If your code is already on GitHub, skip to Step 2.

If not, follow these steps:

```bash
# Navigate to your project directory
cd "/Users/sai/Cargo News"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Railway deployment"

# Create a new repository on GitHub (go to github.com → New Repository)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Important**: Make sure `.env` and `.env.local` files are NOT committed (they're in `.gitignore`)

---

## 🎯 Step 2: Deploy Backend to Railway

### 2.1 Create New Railway Project

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/dashboard
   - Log in with your Railway account

2. **Create New Project**
   - Click the **"+ New Project"** button (top right)
   - Select **"Deploy from GitHub repo"**

3. **Select Your Repository**
   - Railway will show your GitHub repositories
   - **Select your repository** (the one with your Cargo News code)
   - Click **"Deploy Now"**

4. **Railway Auto-Detection**
   - Railway will automatically detect it's a Python project
   - It will use the `railway.json` configuration
   - **Wait for initial build** (this may take 2-3 minutes)

### 2.2 Configure Backend Service

1. **Service Settings**
   - Railway will create a service automatically
   - You should see it building in the dashboard
   - **Wait for build to complete** (check the "Deployments" tab)

2. **Set Root Directory** (if needed)
   - Click on your service
   - Go to **Settings** tab
   - **Root Directory**: Leave empty (or set to `/` if needed)
   - Railway should auto-detect the Python app

### 2.3 Set Environment Variables

1. **Go to Variables Tab**
   - In your backend service, click **"Variables"** tab
   - Click **"+ New Variable"** for each variable below

2. **Add These Variables** (one by one):

   ```
   Variable Name: SUPABASE_URL
   Value: your_supabase_project_url
   ```
   *(Get this from Supabase Dashboard → Settings → API → Project URL)*

   ```
   Variable Name: SUPABASE_KEY
   Value: your_supabase_anon_key
   ```
   *(Get this from Supabase Dashboard → Settings → API → anon public key)*

   ```
   Variable Name: GEMINI_API_KEY
   Value: AIzaSyCSg4pvORmJmdsfPLqmZ41Ia5v9kDNS1Dg
   ```
   *(Get this from Google AI Studio)*

   ```
   Variable Name: SCRAPING_DELAY_SECONDS
   Value: 2
   ```

   ```
   Variable Name: MAX_RETRIES
   Value: 3
   ```

3. **Save Variables**
   - After adding each variable, Railway will automatically redeploy
   - Wait for redeployment to complete

### 2.4 Get Your Backend URL

1. **Go to Settings Tab**
   - Click **"Settings"** in your backend service
   - Scroll down to **"Domains"** section
   - Click **"Generate Domain"** (or use the auto-generated one)
   - **Copy the URL** (e.g., `https://your-app-name.railway.app`)
   - ⚠️ **SAVE THIS URL** - You'll need it for the frontend!

### 2.5 Test Backend

1. **Test Health Endpoint**
   - Open a new browser tab
   - Visit: `https://your-backend-url.railway.app/health`
   - Should see: `{"status": "healthy"}`

2. **Test API**
   - Visit: `https://your-backend-url.railway.app/api/sources`
   - Should see: `[]` (empty array, which is correct if no sources yet)

3. **Check Logs**
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - Check **"Logs"** to see if there are any errors
   - Should see: "Starting up application..." and "Scheduler started successfully"

✅ **Backend is now deployed!**

---

## 🎨 Step 3: Deploy Frontend to Railway

### 3.1 Add Frontend Service

1. **In Same Railway Project**
   - You should still be in your Railway project dashboard
   - Click **"+ New"** button (top right)
   - Select **"GitHub Repo"**

2. **Select Same Repository**
   - Select the **same GitHub repository** you used for backend
   - Click **"Deploy Now"**

3. **Configure Service**
   - Railway will create a new service
   - Wait for it to appear in your project

### 3.2 Configure Frontend Service

1. **Set Root Directory**
   - Click on your **frontend service**
   - Go to **Settings** tab
   - Find **"Root Directory"** field
   - Set it to: `frontend`
   - Click **"Save"**

2. **Verify Build Settings**
   - Railway should auto-detect Next.js
   - Build command should be: `npm install && npm run build`
   - Start command should be: `npm start`
   - If not auto-detected, go to **Settings** → **Build & Deploy** and set manually

### 3.3 Set Frontend Environment Variable

1. **Go to Variables Tab**
   - In your frontend service, click **"Variables"** tab
   - Click **"+ New Variable"**

2. **Add This Variable**:

   ```
   Variable Name: NEXT_PUBLIC_API_URL
   Value: https://your-backend-url.railway.app
   ```
   ⚠️ **Replace `your-backend-url.railway.app` with your actual backend URL from Step 2.4!**

   Example:
   ```
   NEXT_PUBLIC_API_URL=https://cargo-news-backend.railway.app
   ```

3. **Save Variable**
   - Railway will automatically redeploy
   - Wait for redeployment to complete (3-5 minutes for first build)

### 3.4 Get Your Frontend URL

1. **Go to Settings Tab**
   - Click **"Settings"** in your frontend service
   - Scroll down to **"Domains"** section
   - Click **"Generate Domain"** (or use the auto-generated one)
   - **Copy the URL** (e.g., `https://your-frontend-name.railway.app`)

### 3.5 Test Frontend

1. **Visit Frontend URL**
   - Open a new browser tab
   - Visit your frontend URL
   - You should see the articles page (may be empty if no articles yet)

2. **Test Navigation**
   - Click on **"Sources"** link
   - Should see the sources page
   - Try adding a source to test

✅ **Frontend is now deployed!**

---

## ✅ Step 4: Verify Everything Works

### 4.1 Test Complete Flow

1. **Add a Source**
   - Go to your frontend URL
   - Click **"Sources"** in navigation
   - Click **"Add Source"**
   - Enter a URL (e.g., `https://www.stattimes.com/latest-news`)
   - Click **"Add"**
   - Should see success message

2. **Test Scraping**
   - In Sources page, find your added source
   - Click **"Scrape"** button next to it
   - Wait a few minutes
   - Check if articles appear

3. **View Articles**
   - Go back to home page
   - Should see articles listed
   - Click on an article to view details

### 4.2 Check Logs

1. **Backend Logs**
   - Go to backend service → **Deployments** → Latest deployment → **Logs**
   - Should see scraping progress and any errors

2. **Frontend Logs**
   - Go to frontend service → **Deployments** → Latest deployment → **Logs**
   - Should see Next.js build and runtime logs

---

## 🔄 Step 5: Set Up Keep-Alive (Prevent Sleeping)

Railway free tier may sleep after inactivity. To prevent this:

### Option 1: External Cron Service (Recommended)

1. **Go to cron-job.org** (or similar service)
2. **Create a new cron job**:
   - **URL**: `https://your-backend-url.railway.app/keepalive`
   - **Schedule**: Every 5 minutes
   - **Method**: GET
3. **Save and activate**

### Option 2: Railway Pro Plan

- Upgrade to Railway Pro (doesn't sleep)
- Not necessary for testing, but useful for production

---

## 📊 Step 6: Monitor Your Deployment

### 6.1 Railway Dashboard

- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history

### 6.2 Check Health Regularly

- Visit: `https://your-backend-url.railway.app/health`
- Should always return: `{"status": "healthy"}`

---

## 🐛 Troubleshooting

### Backend Not Starting

**Problem**: Backend service shows "Failed" or won't start

**Solutions**:
1. Check **Logs** tab for error messages
2. Verify all environment variables are set correctly
3. Check if `railway.json` is correct
4. Ensure `requirements.txt` is in root directory

### Frontend Not Loading

**Problem**: Frontend shows error or blank page

**Solutions**:
1. Check `NEXT_PUBLIC_API_URL` is set correctly (must be your backend URL)
2. Check frontend logs for build errors
3. Verify `frontend/` directory exists in repository
4. Check if `package.json` is in `frontend/` directory

### Frontend Can't Connect to Backend

**Problem**: Frontend loads but can't fetch data

**Solutions**:
1. Verify `NEXT_PUBLIC_API_URL` matches your backend URL exactly
2. Check backend is running (visit `/health` endpoint)
3. Check CORS settings in backend (should allow all origins)
4. Check browser console for CORS errors

### Scraping Not Working

**Problem**: Scraping button doesn't work or fails

**Solutions**:
1. Check backend logs for scraping errors
2. Verify Supabase and Gemini API keys are correct
3. Check if target website is blocking requests
4. Verify database schema is set up in Supabase

### Playwright Errors

**Problem**: Build fails with Playwright errors

**Solutions**:
1. Check `railway.json` includes `playwright install chromium`
2. Check Railway logs for Playwright installation errors
3. Verify `requirements.txt` includes `playwright==1.40.0`

---

## 📝 Quick Reference

### Your URLs

**Backend URL**: `https://your-backend-name.railway.app`  
**Frontend URL**: `https://your-frontend-name.railway.app`  
**Health Check**: `https://your-backend-name.railway.app/health`

### Environment Variables (Backend)

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=AIzaSyCSg4pvORmJmdsfPLqmZ41Ia5v9kDNS1Dg
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
```

### Environment Variables (Frontend)

```
NEXT_PUBLIC_API_URL=https://your-backend-name.railway.app
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend service created on Railway
- [ ] Backend environment variables set
- [ ] Backend deployed successfully
- [ ] Backend URL copied
- [ ] Backend health check works
- [ ] Frontend service created on Railway
- [ ] Frontend root directory set to `frontend/`
- [ ] Frontend environment variable set (`NEXT_PUBLIC_API_URL`)
- [ ] Frontend deployed successfully
- [ ] Frontend URL works
- [ ] Can add sources via frontend
- [ ] Can scrape articles
- [ ] Articles appear in frontend
- [ ] Keep-alive cron job set up (optional)

---

## 🎉 Congratulations!

Your system is now live and accessible from anywhere!

**Next Steps**:
1. Add your news sources via the web UI
2. Test scraping functionality
3. Monitor logs and metrics
4. Set up custom domains (optional)

---

## 🆘 Need Help?

If you encounter issues:
1. Check Railway logs (most helpful!)
2. Verify all environment variables are set
3. Test backend endpoints directly
4. Check browser console for frontend errors

Good luck with your deployment! 🚀

