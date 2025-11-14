# 🚀 Railway Deployment Guide - Complete System

This guide will help you deploy both the backend (FastAPI) and frontend (Next.js) to Railway.

## 📋 Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app) (free tier available)
3. **Supabase Project** - Already set up with database schema
4. **Google Gemini API Key** - Already obtained

## 🎯 Deployment Strategy

We'll deploy **two separate services** on Railway:
1. **Backend Service** - FastAPI (Python)
2. **Frontend Service** - Next.js (Node.js)

This allows independent scaling and easier management.

---

## 📦 Step 1: Prepare Your Code

### 1.1 Ensure .gitignore is Set Up

Make sure `.gitignore` includes:
```
venv/
__pycache__/
*.pyc
.env
.env.local
node_modules/
.next/
.DS_Store
```

### 1.2 Commit All Code to GitHub

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

---

## 🔧 Step 2: Deploy Backend (FastAPI)

### 2.1 Create New Project on Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will auto-detect Python

### 2.2 Configure Backend Service

Railway should auto-detect:
- **Builder**: NIXPACKS
- **Build Command**: `pip install -r requirements.txt && playwright install chromium`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

✅ The `railway.json` file already has this configured!

### 2.3 Set Environment Variables

In Railway dashboard, go to your backend service → **Variables** tab:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
PORT=8000
```

**Important**: Railway automatically sets `$PORT`, so you don't need to set it manually.

### 2.4 Deploy Backend

1. Railway will automatically start building
2. Wait for build to complete (2-5 minutes)
3. Check **Logs** tab for any errors
4. Once deployed, note your backend URL (e.g., `https://your-app.railway.app`)

### 2.5 Test Backend

Visit: `https://your-backend-url.railway.app/health`

Should return: `{"status": "ok"}`

---

## 🎨 Step 3: Deploy Frontend (Next.js)

### 3.1 Add Frontend Service

1. In the same Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select the **same repository**
3. Railway will detect it's a Node.js project

### 3.2 Configure Frontend Service

**Root Directory**: Set to `frontend/`

**Build Settings**:
- Railway should auto-detect Next.js
- Build command: `npm install && npm run build`
- Start command: `npm start`

### 3.3 Set Frontend Environment Variables

In Railway dashboard, go to your frontend service → **Variables** tab:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

**Important**: Replace `your-backend-url.railway.app` with your actual backend URL from Step 2.4!

### 3.4 Deploy Frontend

1. Railway will automatically start building
2. Wait for build to complete (3-5 minutes)
3. Check **Logs** tab for any errors
4. Once deployed, note your frontend URL (e.g., `https://your-frontend.railway.app`)

### 3.5 Test Frontend

Visit your frontend URL. You should see the articles page!

---

## 🔐 Step 4: Configure CORS (If Needed)

The backend already has CORS configured in `app/main.py`, but verify it allows your frontend domain:

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    # For production, use: allow_origins=["https://your-frontend.railway.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, you might want to restrict CORS to your frontend domain only.

---

## ✅ Step 5: Verify Everything Works

### 5.1 Test Backend Endpoints

```bash
# Health check
curl https://your-backend-url.railway.app/health

# Get sources
curl https://your-backend-url.railway.app/api/sources

# Get articles
curl https://your-backend-url.railway.app/api/articles
```

### 5.2 Test Frontend

1. Visit your frontend URL
2. Check if articles load
3. Try adding a source
4. Test scraping functionality

### 5.3 Test Scraping

1. Go to Sources page
2. Add a test source (if not already added)
3. Click "Scrape" button
4. Check if articles appear

---

## 🔄 Step 6: Set Up Custom Domains (Optional)

### 6.1 Backend Custom Domain

1. In Railway dashboard → Backend service → **Settings** → **Domains**
2. Click **"Generate Domain"** or add custom domain
3. Update frontend `NEXT_PUBLIC_API_URL` if using custom domain

### 6.2 Frontend Custom Domain

1. In Railway dashboard → Frontend service → **Settings** → **Domains**
2. Click **"Generate Domain"** or add custom domain

---

## ⚙️ Step 7: Configure Daily Scraping

The scheduler runs automatically when the backend starts, but Railway free tier may sleep after inactivity.

### Option 1: Keep-Alive Endpoint (Recommended)

Set up an external cron service (like [cron-job.org](https://cron-job.org)) to ping:

```
https://your-backend-url.railway.app/keepalive
```

**Frequency**: Every 5 minutes

### Option 2: Railway Pro Plan

Upgrade to Railway Pro plan which doesn't sleep.

---

## 🐛 Troubleshooting

### Backend Not Starting

1. **Check Logs**: Railway dashboard → Backend service → **Logs**
2. **Verify Environment Variables**: All required vars are set
3. **Check Build Logs**: Look for errors during `pip install` or `playwright install`

### Frontend Not Connecting to Backend

1. **Verify `NEXT_PUBLIC_API_URL`**: Must be your backend URL
2. **Check CORS**: Backend must allow frontend origin
3. **Check Network Tab**: Browser DevTools → Network → Look for failed API calls

### Playwright Not Working

1. **Verify Build Command**: Must include `playwright install chromium`
2. **Check Logs**: Look for Playwright installation errors
3. **Railway Memory**: Playwright needs sufficient memory (Railway free tier should be fine)

### Scraping Not Working

1. **Check Backend Logs**: Look for scraping errors
2. **Verify API Keys**: Supabase and Gemini keys are correct
3. **Check IP Blocking**: Some sites may block Railway's IP (use VPN/proxy if needed)

### Database Connection Issues

1. **Verify Supabase URL/Key**: Check environment variables
2. **Check Supabase Dashboard**: Ensure project is active
3. **Verify RLS Policies**: Make sure policies allow access

---

## 📊 Monitoring

### Railway Dashboard

- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history

### Application Logs

Check Railway logs for:
- Scraping progress
- API errors
- Database connection issues

---

## 💰 Cost Considerations

### Railway Free Tier

- **$5 credit/month** (usually enough for small projects)
- **Pay-as-you-go** after credit
- **Sleeps after inactivity** (use keep-alive to prevent)

### Estimated Monthly Costs

- **Backend**: ~$2-5/month (depending on usage)
- **Frontend**: ~$2-5/month
- **Total**: ~$4-10/month (within free tier credit)

### Supabase

- **Free tier**: 500MB database, 2GB bandwidth
- Should be sufficient for this project

### Google Gemini API

- **Pay-per-use**: ~$0.0014 per article
- **1000 articles/month**: ~$1.40
- Check current pricing at [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🚀 Next Steps After Deployment

1. **Add Your First Source**: Use the web UI to add news sources
2. **Test Scraping**: Manually trigger scraping to verify it works
3. **Set Up Monitoring**: Monitor logs and metrics
4. **Configure Keep-Alive**: Set up cron job to prevent sleeping
5. **Custom Domains**: Add custom domains if desired

---

## 📝 Quick Reference

### Backend URL
```
https://your-backend-url.railway.app
```

### Frontend URL
```
https://your-frontend-url.railway.app
```

### Environment Variables (Backend)
```
SUPABASE_URL=...
SUPABASE_KEY=...
GEMINI_API_KEY=...
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
```

### Environment Variables (Frontend)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

## 🆘 Need Help?

1. **Check Railway Logs**: Most issues are visible in logs
2. **Verify Environment Variables**: Double-check all are set correctly
3. **Test Locally First**: Make sure everything works locally before deploying
4. **Railway Docs**: [docs.railway.app](https://docs.railway.app)

---

## ✅ Deployment Checklist

- [ ] Code committed to GitHub
- [ ] Backend service created on Railway
- [ ] Backend environment variables set
- [ ] Backend deployed and tested
- [ ] Frontend service created on Railway
- [ ] Frontend environment variables set (with backend URL)
- [ ] Frontend deployed and tested
- [ ] CORS configured correctly
- [ ] Keep-alive cron job set up (optional)
- [ ] Custom domains configured (optional)
- [ ] First source added and tested
- [ ] Scraping tested and working

---

**🎉 Congratulations! Your system is now live and accessible from anywhere!**

