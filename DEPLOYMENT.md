# Deployment Guide

This guide will help you deploy the Cargo News Aggregator system to Railway.

## Prerequisites

1. **Supabase Account**: Create a free account at [supabase.com](https://supabase.com)
2. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Railway Account**: Sign up at [railway.app](https://railway.app)
4. **GitHub Account**: For version control and Railway integration

## Step 1: Set Up Supabase Database

1. Create a new project in Supabase
2. Go to SQL Editor and run the SQL script from `database_schema.sql`
3. Note down your Supabase URL and API key from Settings > API

## Step 2: Prepare Your Code

1. Clone or upload your code to GitHub
2. Make sure all files are committed
3. **Important**: The `railway.json` file is already configured to install Playwright browsers during build. No additional setup needed.

## Step 3: Deploy to Railway

### Option A: Deploy from GitHub

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Python project

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Step 4: Configure Environment Variables

In Railway dashboard, go to your project > Variables and add:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
PORT=8000
```

## Step 5: Set Up Daily Scraping

The application uses APScheduler to run daily scraping at 00:00 UTC. The scheduler starts automatically when the app starts.

**Important**: Railway free tier may sleep after inactivity. To prevent this:

1. Use Railway's cron job feature (if available)
2. Or set up an external cron service (like cron-job.org) to ping `/keepalive` endpoint every 5 minutes
3. Or upgrade to Railway Pro plan which doesn't sleep

## Step 6: Deploy Frontend (Optional)

The frontend can be deployed separately:

1. Go to Railway dashboard
2. Add a new service
3. Select your frontend directory
4. Railway will detect Next.js and deploy it
5. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app`

## Step 7: Verify Deployment

1. Check the health endpoint: `https://your-app.railway.app/health`
2. Check the keep-alive endpoint: `https://your-app.railway.app/keepalive`
3. Test the API: `https://your-app.railway.app/api/sources`

## Troubleshooting

### App Not Starting

- Check Railway logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is correct

### Scheduler Not Running

- Check application logs
- Verify APScheduler is installed
- Check timezone settings (should be UTC)

### Database Connection Issues

- Verify Supabase URL and key are correct
- Check Supabase project is active
- Ensure database schema is created

### Scraping Fails

- Check if target websites are blocking requests
- Verify network connectivity
- Review scraper logs for specific errors

## Monitoring

- Use Railway's built-in logs dashboard
- Set up error tracking (optional: Sentry)
- Monitor API usage for Gemini API

## Cost Considerations

- **Railway**: Free tier available, pay-as-you-go pricing
- **Supabase**: Free tier includes 500MB database
- **Google Gemini API**: Pay-per-use pricing, check current rates

## Next Steps

1. Add your first news source via the web UI or API
2. Test manual scraping: `POST /api/scrape/all`
3. Monitor the first daily scrape at 00:00 UTC
4. Customize scrapers for additional news sources

