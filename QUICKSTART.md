# Quick Start Guide

Get your Cargo News Aggregator up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed (for frontend)
- [ ] Supabase account created
- [ ] Google Gemini API key obtained
- [ ] Railway account (for deployment)

## Step 1: Database Setup (5 minutes)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for project to be ready
3. Go to SQL Editor
4. Copy and paste the entire contents of `database_schema.sql`
5. Click "Run"
6. Go to Settings > API and copy:
   - Project URL → `https://akvdrlzezeqqutdcvbjv.supabase.co`
   - anon/public key → `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFrdmRybHplemVxcXV0ZGN2Ymp2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwMDIwMDUsImV4cCI6MjA3ODU3ODAwNX0.uLMMuYnUVdiKpo5HcOVmNHam8O8wC3hiAAfhx0GSuY4`

## Step 2: Get Gemini API Key (2 minutes)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key → `AIzaSyBZBJqB3NRgM4LfjslXE96p9vfv01l6FBA`

## Step 3: Local Setup (3 minutes)

### Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your keys

# Run backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## Step 4: Add Your First Source

1. Open browser: `http://localhost:3000`
2. Click "Sources" in navigation
3. Click "Add Source"
4. Enter:
   - URL: `https://www.aircargonews.net/news`
   - Name: `Air Cargo News`
5. Click "Add Source"
6. Click "Test" to verify it works

## Step 5: Scrape Articles

### Option A: Via Web UI
- Go to Sources page
- Click "Test" (this will scrape a few articles)

### Option B: Via API
```bash
# Get source ID from Sources page, then:
curl -X POST http://localhost:8000/api/scrape/{source_id}
```

## Step 6: View Articles

1. Go to home page: `http://localhost:3000`
2. Articles will appear after scraping completes
3. Use tag filters on the left to filter articles
4. Click an article to view full details

## Step 7: Deploy to Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Select your repository
5. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GEMINI_API_KEY`
6. Deploy!

## Troubleshooting

**Backend won't start?**
- Check `.env` file exists and has all required variables
- Verify Supabase project is active
- Check Python version: `python --version`

**Frontend can't connect?**
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for errors

**Scraping fails?**
- Some sites block automated requests
- Try increasing `SCRAPING_DELAY_SECONDS` in `.env`
- Check scraper logs in terminal

**No articles showing?**
- Verify scraping completed successfully
- Check database in Supabase dashboard
- Try manual scrape via API

## Next Steps

- Add more news sources
- Customize AI prompt for better summaries
- Set up daily automatic scraping
- Customize frontend styling
- Add more scrapers for other sites

## Need Help?

- Check `SETUP.md` for detailed setup
- Check `DEPLOYMENT.md` for deployment guide
- Review `PROJECT_SUMMARY.md` for architecture overview
- Check Railway logs for errors
- Review Supabase logs for database issues

Happy scraping! 🚀

