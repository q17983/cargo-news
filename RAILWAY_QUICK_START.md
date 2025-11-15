# 🚀 Railway Quick Start Checklist

## ⚡ 5-Minute Deployment

### Step 1: Backend Deployment (2 minutes)

1. **Go to Railway**: [railway.app/dashboard](https://railway.app/dashboard)
2. **New Project** → **Deploy from GitHub repo**
3. **Select your repository**
4. **Set Environment Variables**:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GEMINI_API_KEY=AIzaSyCSg4pvORmJmdsfPLqmZ41Ia5v9kDNS1Dg
   SCRAPING_DELAY_SECONDS=2
   MAX_RETRIES=3
   ```
5. **Wait for deployment** (2-3 minutes)
6. **Copy backend URL** (e.g., `https://your-app.railway.app`)

### Step 2: Frontend Deployment (2 minutes)

1. **In same Railway project**, click **"+ New"** → **"GitHub Repo"**
2. **Select same repository**
3. **Set Root Directory**: `frontend/`
4. **Set Environment Variable**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
   ⚠️ **Replace with your actual backend URL from Step 1!**
5. **Wait for deployment** (3-5 minutes)
6. **Copy frontend URL**

### Step 3: Test (1 minute)

1. **Visit frontend URL** → Should see articles page
2. **Visit backend URL/health** → Should see `{"status": "healthy"}`
3. **Add a source** → Test scraping

## ✅ Done!

Your system is now live and accessible from anywhere!

## 🔧 Troubleshooting

**Frontend not loading?**
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running (visit `/health`)

**Backend not starting?**
- Check environment variables are set
- Check Railway logs for errors

**Scraping not working?**
- Check backend logs
- Verify API keys are correct

## 📚 Full Guide

See `RAILWAY_DEPLOYMENT_GUIDE.md` for detailed instructions.

