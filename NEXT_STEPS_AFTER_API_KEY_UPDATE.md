# ✅ Next Steps After Updating API Key

## Current Status
- ✅ Local `.env` file updated with new API key
- ✅ All hardcoded keys removed from documentation
- ⏳ **Next: Update Railway and Test**

---

## Step 1: Update Railway Environment Variable

### Option A: Via Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**
   - Navigate to: https://railway.app/dashboard
   - Select your **Backend Service** (the Python/FastAPI service, not frontend)

2. **Update the API Key**
   - Click on **"Variables"** tab
   - Find `OPENAI_API_KEY` in the list
   - Click on it to edit
   - **Paste your new API key** (the same one you put in `.env`)
   - Click **"Save"**
   - Railway will automatically redeploy the service (takes 2-3 minutes)

3. **Wait for Redeployment**
   - Watch the deployment logs
   - Wait until you see "Deployment successful" or similar

### Option B: Via Railway CLI (If you have it installed)

```bash
railway variables set OPENAI_API_KEY=your_new_key_here
```

---

## Step 2: Test Local Setup

Test that your local scripts work with the new API key:

```bash
# Test the aircargonews scraper
python3 scrape_aircargonews.py --max-pages 1

# Test the stattimes scraper  
python3 scrape_stattimes.py --max-pages 1
```

**Expected Result:**
- ✅ Scripts run successfully
- ✅ Articles are scraped
- ✅ AI summaries are generated (no "403 API key leaked" errors)
- ✅ Articles are saved to database

---

## Step 3: Test Railway Backend

After Railway redeploys:

1. **Check Railway Logs**
   - Go to Railway Dashboard → Your Backend Service → Logs
   - Look for any API key errors
   - Should see successful scraping logs

2. **Test via Frontend**
   - Go to your frontend URL
   - Try triggering a scrape from the web interface
   - Verify articles are being scraped and summarized

3. **Test via API** (Optional)
   ```bash
   # Replace with your Railway backend URL
   curl https://your-backend-url.railway.app/api/health
   ```

---

## Step 4: Verify Everything Works

### ✅ Checklist

- [ ] Railway `OPENAI_API_KEY` updated
- [ ] Railway redeployment completed (2-3 minutes)
- [ ] Local test: `scrape_aircargonews.py` works
- [ ] Local test: `scrape_stattimes.py` works
- [ ] No "403 API key leaked" errors
- [ ] Articles are being summarized (not just saved without summaries)
- [ ] Railway backend logs show no API key errors
- [ ] Frontend scraping works

---

## 🐛 Troubleshooting

### If you still see "403 API key leaked" errors:

1. **Double-check the API key**
   - Make sure it's the same in both `.env` and Railway
   - No extra spaces or quotes
   - Copy-paste directly from Google AI Studio

2. **Verify Railway has the new key**
   - Go to Railway → Variables
   - Check `OPENAI_API_KEY` value
   - Make sure it matches your `.env` file

3. **Wait for Railway redeployment**
   - Sometimes it takes a few minutes
   - Check deployment logs to confirm it finished

4. **Check if the key is valid**
   - Go to: https://aistudio.google.com/apikey
   - Verify the key is active and not revoked

### If local tests work but Railway doesn't:

- Railway might still be using the old key
- Wait a bit longer for redeployment
- Check Railway logs for errors
- Try manually redeploying: Railway → Deployments → Redeploy

---

## 📝 Important Reminders

1. **Never commit API keys to Git** ✅ (Already fixed)
2. **Always use environment variables** ✅ (Already set up)
3. **Keep `.env` in `.gitignore`** ✅ (Already configured)
4. **Use placeholders in documentation** ✅ (Already updated)

---

## 🎉 You're Done When:

- ✅ Local scripts work with new API key
- ✅ Railway has the new API key
- ✅ Railway backend redeployed successfully
- ✅ No API key errors in logs
- ✅ Articles are being scraped and summarized correctly

---

**Need Help?** Check `API_KEY_SECURITY_GUIDE.md` for more details on security best practices.

