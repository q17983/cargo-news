# Gemini API Quota Management Guide

## ⚠️ Quota Exceeded Error

If you're seeing "quota exceeded" errors, here's what happened and how to fix it.

## Common Causes

1. **Too many articles scraped at once**
   - First-time scrape was set to 100 pages (potentially 1000+ articles)
   - Each article = 1 Gemini API call
   - Free tier has limited requests per minute/day

2. **No rate limiting**
   - API calls were made too quickly
   - No delay between calls

3. **Re-processing existing articles**
   - If duplicate check fails, articles get re-summarized

## ✅ Fixes Implemented

### 1. Rate Limiting
- Added 1-second minimum delay between Gemini API calls
- Prevents hitting rate limits too quickly

### 2. Reduced First-Time Scrape
- Changed from 100 pages to **20 pages** for first scrape
- Still checks duplicates to avoid re-processing
- Prevents quota exhaustion on initial setup

### 3. Quota Error Detection
- Detects quota errors and stops scraping immediately
- Logs partial success instead of continuing
- Prevents wasting more API calls

### 4. Better Duplicate Checking
- Always checks duplicates (even on first scrape)
- Prevents re-summarizing existing articles

## 📊 Google Gemini API Limits

### Free Tier (Typical Limits)
- **Requests per minute**: ~15-60 requests
- **Requests per day**: Varies (check your Google Cloud Console)
- **Tokens per day**: Limited (check your quota)

### Paid Tier
- Higher limits
- More requests per minute/day
- Check Google Cloud Console for your specific limits

## 🔧 How to Check Your Quota

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Quotas**
3. Search for "Generative Language API"
4. Check your current usage and limits

## 💡 Solutions

### Option 1: Wait and Resume
- Quota typically resets daily (or hourly for per-minute limits)
- Wait a few hours and try again
- The scraper will continue from where it stopped

### Option 2: Upgrade API Plan
- Upgrade to a paid tier in Google Cloud Console
- Higher quotas = more articles per day

### Option 3: Reduce Scraping Volume
- Scrape fewer pages at a time
- Use `--max-pages` parameter to limit pages
- Example: `python3 scrape_stattimes.py --max-pages 5`

### Option 4: Stagger Scraping
- Scrape one source at a time
- Wait between sources
- Spread scraping across multiple days

## 🛠️ Current Settings

- **Rate limiting**: 1 second delay between API calls
- **First-time scrape**: 20 pages max (was 100)
- **Daily scrape**: 3 pages max
- **Duplicate checking**: Always enabled

## 📝 Recommendations

1. **For initial setup**: Scrape sources one at a time
2. **Monitor quota**: Check Google Cloud Console regularly
3. **Use daily scraping**: Let the daily scheduler handle updates (3 pages = ~15-30 articles)
4. **Manual scraping**: Use `--max-pages` to limit when testing

## 🚨 If Quota is Still Exceeded

1. **Stop all scraping** (close scripts, stop server)
2. **Wait 24 hours** for quota reset
3. **Check your quota** in Google Cloud Console
4. **Resume with smaller batches** (use `--max-pages 5`)

## Example: Safe Scraping Command

```bash
# Scrape only 5 pages (safer for quota)
python3 scrape_stattimes.py --max-pages 5

# Or scrape one source at a time via web UI
# Click "Scrape" button for one source, wait, then next source
```

