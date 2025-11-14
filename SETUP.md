# Local Setup Guide

Follow these steps to set up the Cargo News Aggregator system locally.

## Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend)
- Supabase account
- Google Gemini API key

## Backend Setup

1. **Clone the repository** (if not already done)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GEMINI_API_KEY=your_gemini_api_key
   SCRAPING_DELAY_SECONDS=2
   MAX_RETRIES=3
   ```

5. **Set up Supabase database**:
   - Create a new project in Supabase
   - Go to SQL Editor
   - Run the SQL from `database_schema.sql`

6. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Testing the System

1. **Add a news source**:
   - Go to `http://localhost:3000/sources`
   - Click "Add Source"
   - Enter: `https://www.aircargonews.net/news`
   - Name: `Air Cargo News`

2. **Test scraping**:
   - Click "Test" next to the source to verify it works
   - Or use the API: `POST http://localhost:8000/api/scrape/{source_id}`

3. **View articles**:
   - Go to `http://localhost:3000`
   - Articles will appear after scraping completes

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Import Errors

If you get import errors, make sure:
- Virtual environment is activated
- All dependencies are installed
- You're in the project root directory

### Database Connection Issues

- Verify Supabase URL and key in `.env`
- Check Supabase project is active
- Ensure database schema is created

### Scraping Issues

- Some websites may block automated requests
- Check scraper logs for specific errors
- Try increasing `SCRAPING_DELAY_SECONDS`

### Frontend Not Connecting

- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

## Development Tips

- Backend auto-reloads with `--reload` flag
- Frontend hot-reloads automatically
- Check logs in terminal for debugging
- Use API documentation at `/docs` for testing endpoints

