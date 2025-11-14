# Supported Air Cargo News Websites

This document lists all supported air cargo news websites and their custom scrapers.

## Currently Supported Sites

### 1. Air Cargo News (aircargonews.net)
- **URL**: `https://www.aircargonews.net`
- **Scraper**: `AircargonewsScraper`
- **Listing URL**: `https://www.aircargonews.net/latest-news/31.more?navcode=28`
- **Status**: ✅ Fully supported with custom scraper
- **Features**:
  - Extracts articles from latest-news listing page
  - Handles pagination (up to 10 pages)
  - Filters out category pages
  - Extracts only main article content (excludes related articles)
  - Smart pagination (100 pages first time, 3 pages daily with early stopping)

### 2. Air Cargo Week (aircargoweek.com)
- **URL**: `https://aircargoweek.com`
- **Scraper**: `AircargoweekScraper`
- **Listing URL**: `https://aircargoweek.com/news/`
- **Status**: ✅ Fully supported with custom scraper
- **Features**:
  - Uses Playwright to handle JavaScript and anti-bot blocking
  - Extracts articles from news listing page
  - Handles "Load more" button for pagination
  - Article URLs are direct slugs (e.g., `/article-title-slug/`)
  - Smart pagination (handles first-time vs daily scraping)

### 3. STAT Times (stattimes.com)
- **URL**: `https://www.stattimes.com`
- **Scraper**: `StattimesScraper`
- **Listing URL**: `https://www.stattimes.com/latest-news`
- **Status**: ✅ Fully supported with custom scraper
- **Features**:
  - Extracts articles from latest-news listing page
  - Handles pagination (numbered pages: /latest-news, /latest-news/2, etc.)
  - Article URLs pattern: `/{category}/{title-slug}-{numeric-id}`
  - Extracts article content, title, and date
  - Smart pagination (100 pages first time, 3 pages daily with early stopping)

## Adding New Sites

Each air cargo news website requires its own custom scraper because:
- Website structures are completely different
- HTML/CSS selectors vary significantly
- Pagination mechanisms differ
- Anti-bot measures vary

### Steps to Add Support:

1. **Create Custom Scraper**: `app/scraper/[sitename]_scraper.py`
2. **Register in Factory**: Add to `app/scraper/scraper_factory.py`
3. **Test Thoroughly**: Verify article extraction works correctly
4. **Update This List**: Add the site to this document

See `app/scraper/README.md` for detailed instructions.

## Sites Needing Custom Scrapers

If you add a source for a site without a custom scraper:
- It will use `BaseScraper` (generic scraper)
- May not work well - generic scrapers have limited functionality
- You should create a custom scraper for best results

## Notes

- Each scraper is a separate Python file to avoid confusion
- Scrapers are automatically selected based on URL domain
- The system shows which scraper is being used in the UI
- Listing URLs are automatically transformed (e.g., homepage → latest-news page)

