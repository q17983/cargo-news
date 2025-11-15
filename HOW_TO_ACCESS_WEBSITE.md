# 🌐 How to Access Your Website on Railway

## Quick Steps

### 1. Get Your Frontend URL

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click on your Frontend Service** (the one that just deployed successfully)
3. **Go to "Settings" tab**
4. **Scroll down to "Domains" section**
5. **You'll see your Railway URL**, something like:
   ```
   https://cargo-news-frontend-production.up.railway.app
   ```
6. **Click on the URL** or copy it to your browser

### 2. Verify Backend Connection

Before accessing, make sure your frontend can connect to the backend:

1. **In your Frontend Service**, go to **"Variables" tab**
2. **Check that you have**:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.railway.app
   ```
   ⚠️ **Replace `your-backend-url.railway.app` with your actual backend URL!**

3. **To find your backend URL**:
   - Go to your **Backend Service** in Railway
   - Go to **"Settings"** → **"Domains"**
   - Copy the URL (e.g., `https://web-production-1349.up.railway.app`)

4. **Update Frontend Variable**:
   - Go back to **Frontend Service** → **"Variables"**
   - Update `NEXT_PUBLIC_API_URL` to your backend URL
   - Railway will automatically redeploy

### 3. Access Your Website

Once the frontend is deployed and the environment variable is set:

1. **Open your browser**
2. **Go to your frontend URL** (from Step 1)
3. **You should see your Cargo News website!**

---

## 🔍 Troubleshooting

### If the website doesn't load:

1. **Check Deployment Status**:
   - Go to **"Deployments" tab** in Railway
   - Make sure the latest deployment shows **"Active"** (green checkmark)

2. **Check Logs**:
   - Click on the latest deployment
   - Check **"Logs"** tab
   - Look for errors (should see "Starting Container" and no errors)

3. **Verify Environment Variable**:
   - Make sure `NEXT_PUBLIC_API_URL` is set correctly
   - No trailing slash in the URL!
   - Should be: `https://your-backend-url.railway.app` (NOT `https://your-backend-url.railway.app/`)

4. **Test Backend First**:
   - Visit: `https://your-backend-url.railway.app/health`
   - Should see: `{"status": "healthy"}`
   - If backend doesn't work, fix that first

### If you see "Failed to fetch" errors:

- **Backend URL is wrong**: Check `NEXT_PUBLIC_API_URL` in frontend variables
- **Backend is down**: Check backend service status in Railway
- **CORS issue**: Backend should have CORS enabled (already configured)

---

## 📝 Quick Checklist

- [ ] Frontend service is deployed and active
- [ ] Frontend URL is generated in Railway Settings → Domains
- [ ] Backend service is deployed and active
- [ ] Backend URL is known
- [ ] `NEXT_PUBLIC_API_URL` is set in frontend variables (points to backend)
- [ ] Both services show "Active" status
- [ ] Can access frontend URL in browser
- [ ] Can see the website (even if no articles yet)

---

## 🎯 Expected URLs

You should have **TWO** Railway URLs:

1. **Backend URL**: `https://web-production-1349.up.railway.app` (or similar)
   - Used for API calls
   - Set in frontend's `NEXT_PUBLIC_API_URL` variable

2. **Frontend URL**: `https://cargo-news-frontend-production.up.railway.app` (or similar)
   - This is your website URL
   - Users visit this URL

---

## 🚀 Next Steps After Accessing

Once you can access the website:

1. **Add News Sources**:
   - Go to `/sources` page
   - Add your news sources (Air Cargo News, Air Cargo Week, STAT Times)

2. **Scrape Articles**:
   - Click "Scrape All Sources" button
   - Wait for articles to be scraped and summarized

3. **View Articles**:
   - Go to home page (`/`)
   - Filter by source or tags
   - Click on articles to read summaries

---

## 💡 Pro Tip

**Bookmark your frontend URL** - it's your website's address!

You can also set up a custom domain in Railway Settings → Domains if you have one.

