# 🔑 API Keys Reference

## Current API Keys Configuration

### OpenAI API Key
**Key**: `YOUR_OPENAI_API_KEY_HERE` (⚠️ Never commit actual keys to Git!)

**Where to Set:**
- **Railway**: Backend Service → Variables → `OPENAI_API_KEY`
- **Local Development**: `.env` file → `OPENAI_API_KEY`

**Last Updated**: 2025-11-15

---

## How to Update API Keys in Railway

### Step 1: Go to Railway Dashboard
1. Navigate to: https://railway.app/dashboard
2. Select your **Backend Service** (Python/FastAPI service)

### Step 2: Update Environment Variable
1. Click on **"Variables"** tab
2. Find `OPENAI_API_KEY` in the list
3. Click on it to edit
4. Update the value to your actual API key (get it from https://aistudio.google.com/apikey)
5. Click **"Save"**
6. Railway will automatically redeploy the service

### Step 3: Verify
1. Wait for redeployment to complete (2-3 minutes)
2. Check deployment logs for any errors
3. Test scraping to verify API key works

---

## Security Notes

⚠️ **Important:**
- API keys are stored in Railway environment variables (NOT in code)
- Never commit API keys to Git
- `.env` files are in `.gitignore` and should not be committed
- If an API key is exposed, regenerate it immediately

---

## All Required Environment Variables

### Backend Service (Railway)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_actual_openai_api_key_here
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
PORT=8000
```

### Frontend Service (Railway)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

## Testing API Key

After updating the API key, test it by:

1. **Trigger a scrape** from the frontend
2. **Check scraping logs** in Railway
3. **Verify articles are being summarized** (not failing with API errors)

If you see "quota exceeded" or "API key invalid" errors, verify the key is correct.

