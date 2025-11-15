# 🚀 Deploy to Railway - Right Now!

Your code is on GitHub: https://github.com/q17983/cargo-news

## Step 1: Deploy Backend (5 minutes)

### 1.1 Create Railway Project
1. Go to: https://railway.app/dashboard
2. Click **"+ New Project"** (top right)
3. Select **"Deploy from GitHub repo"**
4. Find and select: **q17983/cargo-news**
5. Click **"Deploy Now"**

### 1.2 Wait for Build
- Railway will automatically detect Python
- Build will take 2-3 minutes
- Watch the "Deployments" tab

### 1.3 Set Environment Variables
Once build starts, go to **"Variables"** tab and add:

```
SUPABASE_URL = your_supabase_project_url
SUPABASE_KEY = your_supabase_anon_key
GEMINI_API_KEY = AIzaSyCSg4pvORmJmdsfPLqmZ41Ia5v9kDNS1Dg
SCRAPING_DELAY_SECONDS = 2
MAX_RETRIES = 3
```

**Where to get these:**
- **Supabase URL & Key**: Supabase Dashboard → Settings → API
- **Gemini API Key**: Google AI Studio

### 1.4 Get Backend URL
1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. **Copy the URL** (e.g., `https://cargo-news-production.up.railway.app`)
5. ⚠️ **SAVE THIS URL** - You'll need it for frontend!

### 1.5 Test Backend
Visit: `https://your-backend-url.railway.app/health`
Should see: `{"status": "healthy"}`

---

## Step 2: Deploy Frontend (5 minutes)

### 2.1 Add Frontend Service
1. In the **same Railway project**, click **"+ New"**
2. Select **"GitHub Repo"**
3. Select **q17983/cargo-news** again
4. Click **"Deploy Now"**

### 2.2 Configure Frontend
1. Click on the **new service** (frontend)
2. Go to **"Settings"** tab
3. Find **"Root Directory"**
4. Set it to: `frontend`
5. Click **"Save"**

### 2.3 Set Frontend Environment Variable
1. Go to **"Variables"** tab
2. Click **"+ New Variable"**
3. Add:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.railway.app
   ```
   ⚠️ **Replace with your actual backend URL from Step 1.4!**

### 2.4 Wait for Deployment
- Frontend build takes 3-5 minutes
- Watch the "Deployments" tab

### 2.5 Get Frontend URL
1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. **Copy the URL**

### 2.6 Test Frontend
Visit your frontend URL - you should see the articles page!

---

## Step 3: Test Everything

1. **Visit Frontend URL**
2. **Go to Sources page**
3. **Add a source**: `https://www.stattimes.com/latest-news`
4. **Click "Scrape"**
5. **Wait and check if articles appear**

---

## ✅ Done!

Your system is now live and accessible from anywhere!

---

## 🐛 Troubleshooting

**Backend not starting?**
- Check "Logs" tab for errors
- Verify all environment variables are set

**Frontend not loading?**
- Check `NEXT_PUBLIC_API_URL` matches backend URL exactly
- Check frontend logs

**Can't connect?**
- Verify backend is running (visit `/health`)
- Check CORS settings

---

## 📝 Your URLs

**Backend**: `https://your-backend-url.railway.app`  
**Frontend**: `https://your-frontend-url.railway.app`  
**GitHub**: `https://github.com/q17983/cargo-news`

