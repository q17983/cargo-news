# How the System Works When Adding New Sources

## Current Flow

When you add a new source via the web UI:

### 1. Source Creation
- You enter a URL (and optionally a name) in the web UI
- The system saves it to the database
- **The scraper factory automatically detects which scraper to use** based on the URL domain

### 2. Scraper Selection (Automatic)
The `ScraperFactory` automatically selects the appropriate scraper:

- **aircargonews.net** → Uses `AircargonewsScraper` (custom scraper)
- **Other domains** → Uses `BaseScraper` (generic scraper, may need customization)

The factory checks the domain name and routes to the correct scraper automatically.

### 3. Scraping Trigger
Currently, scraping does **NOT** automatically start. You have two options:

**Option A: Manual Trigger**
- Click "Test" button next to the source (tests connection)
- Or manually trigger via API: `POST /api/scrape/{source_id}`

**Option B: Auto-Scrape (New Feature)**
- Check "Automatically start scraping after adding" when creating source
- Scraping will start immediately in the background

**Option C: Wait for Daily Schedule**
- The daily scheduler (00:00 UTC) will automatically scrape all active sources
- New sources will be included in the next scheduled run

## How Scraper Selection Works

```python
# When you add: https://www.aircargonews.net
ScraperFactory.create_scraper(url)
  → Detects "aircargonews.net" in domain
  → Returns AircargonewsScraper instance

# When you add: https://example-news.com  
ScraperFactory.create_scraper(url)
  → No specific scraper found
  → Returns BaseScraper (generic)
```

## For New Sites (Without Custom Scraper)

If you add a source for a site that doesn't have a custom scraper:

1. **It will use BaseScraper** (generic scraper)
2. **May not work well** - BaseScraper has limited functionality
3. **You need to create a custom scraper** for best results

### Steps to Add Support for a New Site:

1. Create `app/scraper/[sitename]_scraper.py`
2. Register it in `app/scraper/scraper_factory.py`
3. Test it works correctly
4. Then add the source via web UI - it will automatically use the new scraper

See `app/scraper/README.md` for detailed instructions.

## Example Flow

1. **User adds source**: `https://www.aircargonews.net` via web UI
2. **System saves** to database with `is_active=True`
3. **Scraper factory** detects domain → uses `AircargonewsScraper`
4. **If auto-scrape enabled**: Scraping starts immediately
5. **Otherwise**: Wait for manual trigger or daily schedule
6. **Daily schedule**: All active sources are scraped at 00:00 UTC

## Important Notes

- **Duplicate prevention**: Already scraped articles are automatically skipped
- **Scraper selection**: Happens automatically based on URL domain
- **No code changes needed**: For sites with existing scrapers (like aircargonews.net)
- **Code changes needed**: For new sites without custom scrapers

