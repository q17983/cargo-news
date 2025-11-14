# Smart Pagination System

The scraper now uses intelligent pagination that adapts based on whether it's the first scrape or a daily update.

## How It Works

### First-Time Scraping
When a source has **no existing articles** in the database:
- **Scrapes up to 100 pages** to get historical articles
- **Doesn't check for duplicates** during pagination (faster)
- Gets all available articles from the site

### Daily Scraping
When a source **already has articles** in the database:
- **Scrapes up to 3 pages** (since only 10-15 new articles per day)
- **Checks for duplicates as it goes** - stops early when finding old articles
- **Stops after 2 consecutive pages** with all duplicates
- Much faster - only processes new articles

## Example Flow

### First Run (No Articles in DB)
```
Page 1: Found 20 articles → All new → Continue
Page 2: Found 20 articles → All new → Continue
...
Page 100: Found 20 articles → All new → Continue
Total: ~2000 articles scraped
```

### Daily Run (Has Articles in DB)
```
Page 1: Found 20 articles → 5 new, 15 duplicates → Continue (found new articles)
Page 2: Found 20 articles → 3 new, 17 duplicates → Continue (found new articles)
Page 3: Found 20 articles → 0 new, 20 duplicates → Stop (all duplicates)
Total: 8 new articles scraped (much faster!)
```

## Benefits

1. **Efficient First Run**: Gets all historical articles in one go
2. **Fast Daily Updates**: Only scrapes what's needed (first few pages)
3. **Early Stopping**: Automatically stops when reaching old articles
4. **No Wasted Time**: Doesn't scrape pages with only duplicates

## Configuration

The system automatically detects:
- **First scrape**: Checks if source has any articles (`get_articles_by_source`)
- **Daily scrape**: Uses smart duplicate checking

You can adjust these values in `app/api/routes/scrape.py`:
- `max_pages = 100` for first-time scraping
- `max_pages = 3` for daily scraping
- `max_consecutive_duplicates = 2` (stop after 2 pages of all duplicates)

## For aircargonews.net

- **First time**: Scrapes up to 100 pages (~2000 articles)
- **Daily**: Scrapes first 3 pages, stops early if all duplicates found
- **Typical daily**: Only 1-2 pages needed (10-15 new articles)

