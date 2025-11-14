# Duplicate Article Prevention

The system has multiple layers of duplicate detection to ensure articles are not scraped and saved multiple times.

## How It Works

### 1. URL-Based Detection (Primary)
- **When**: Before scraping the article
- **Method**: Checks if an article with the same URL already exists in the database
- **Advantage**: Fast and reliable - URLs are unique identifiers
- **Location**: `app/database/supabase_client.py::article_exists()`

### 2. Title-Based Detection (Secondary)
- **When**: After scraping, before saving
- **Method**: Compares the article title with existing articles (checks recent 100 articles for performance)
- **Advantage**: Catches duplicates even if URL format changed
- **Similarity Threshold**: 90% word match
- **Location**: `app/database/supabase_client.py::article_exists()` and `_titles_similar()`

### 3. Database Constraint
- **URL Uniqueness**: The database has a UNIQUE constraint on the `url` column
- **Prevention**: Even if duplicate detection fails, the database will reject duplicate URLs

## Daily Scraping Behavior

When the system runs daily at 00:00 UTC:

1. **Fetches article URLs** from listing pages
2. **Checks each URL** against the database (fast check)
3. **Skips if exists**: Logs "Article already exists (by URL)" and continues
4. **Scrapes if new**: Only scrapes articles that don't exist
5. **Double-checks by title**: After scraping, verifies title doesn't match existing articles
6. **Saves only new articles**: Prevents duplicates from being saved

## Performance Optimization

- Title checking is limited to the **most recent 100 articles** to maintain performance
- URL checking uses database indexes for fast lookups
- Duplicate checks happen **before** expensive operations (scraping, AI summarization)

## Logging

The system logs when duplicates are detected:
- `"Article already exists (by URL): [url]"`
- `"Article already exists (by title): [title]..."`

Check the backend logs to see how many duplicates were skipped during each scraping run.

## Manual Testing

To test duplicate detection:

```python
from app.database.supabase_client import db

# Test URL check
exists = db.article_exists("https://example.com/article")
print(f"URL exists: {exists}")

# Test title check
exists = db.article_exists("https://example.com/article", title="Test Article Title")
print(f"Title exists: {exists}")
```

## Troubleshooting

**Issue**: Duplicates still appearing
- Check if URLs are being normalized (trailing slashes, http vs https)
- Verify database UNIQUE constraint is working
- Check logs for duplicate detection messages

**Issue**: Too many false positives (legitimate articles marked as duplicates)
- Adjust similarity threshold in `_titles_similar()` method
- Review title normalization logic

