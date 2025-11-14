# Gemini API Pricing & Quota Explanation

## ⚠️ Why "Quota Exceeded" Still Shows

The "quota exceeded" warning **persists** because it's stored in your **Supabase database** as a scraping log record. It shows the **LAST scraping attempt** that failed due to quota limits.

### Where It's Stored
- **Table**: `scraping_logs` in Supabase
- **Field**: `error_message` contains "Gemini API quota exceeded..."
- **Status**: `status = 'partial'` (meaning some articles were processed before hitting quota)

### Why It Still Shows
- The error message is **historical data** - it records what happened during the last scrape
- It doesn't mean you're currently hitting quota limits
- It's displayed to inform you about past scraping issues

### How to Clear It
The error will disappear when:
1. **A new successful scrape runs** - The latest log will replace it
2. **Manually delete the log** - Go to Supabase dashboard → `scraping_logs` table → Delete the record with the error
3. **Wait for quota reset** - Once quota resets and you scrape successfully, the new log will show success

---

## 💰 Gemini API Pricing (2025)

### Model: `gemini-2.0-flash` (Current Model Used)

**Input Pricing:**
- **Free Tier**: $0 per 1M tokens (up to quota limits)
- **Paid Tier**: $0.075 per 1M input tokens

**Output Pricing:**
- **Free Tier**: $0 per 1M tokens (up to quota limits)
- **Paid Tier**: $0.30 per 1M output tokens

### Typical Article Processing

**Average Article:**
- **Input**: ~5,000-10,000 tokens (article content + prompt)
- **Output**: ~1,000-2,000 tokens (summary in Traditional Chinese)

**Cost Per Article (Paid Tier):**
- Input: 10,000 tokens = $0.00075
- Output: 2,000 tokens = $0.0006
- **Total: ~$0.00135 per article** (approximately **$0.0014 USD**)

### Cost Examples

| Articles | Input Tokens | Output Tokens | Cost (USD) |
|----------|-------------|---------------|------------|
| 1 article | 10,000 | 2,000 | $0.0014 |
| 10 articles | 100,000 | 20,000 | $0.014 |
| 100 articles | 1,000,000 | 200,000 | $0.14 |
| 1,000 articles | 10,000,000 | 2,000,000 | $1.40 |
| 10,000 articles | 100,000,000 | 20,000,000 | $14.00 |

### Monthly Cost Estimate

**Daily Scraping (3 pages = ~15-30 articles/day):**
- 30 articles/day × 30 days = 900 articles/month
- **Cost: ~$1.26/month**

**First-Time Scrape (20 pages = ~200-400 articles):**
- 400 articles
- **Cost: ~$0.56**

---

## 📊 Free Tier Quota Limits

### Google Gemini API Free Tier

**Typical Limits (varies by account):**
- **Requests per minute**: 15-60 requests
- **Requests per day**: 1,500-2,000 requests
- **Tokens per day**: ~1.5M-2M tokens

**What This Means:**
- You can process **~150-200 articles per day** on free tier
- After that, you'll hit quota limits
- Quota typically resets **daily** (at midnight UTC or your timezone)

---

## 🔧 How to Check Your Quota

1. **Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Navigate to: **APIs & Services** → **Quotas**
   - Search for: "Generative Language API"
   - Check: Current usage vs. limits

2. **Supabase Dashboard**
   - Check `scraping_logs` table
   - Look for `error_message` containing "quota"
   - See when the last quota error occurred

---

## 💡 Cost Optimization Tips

1. **Use Free Tier Wisely**
   - Spread scraping across multiple days
   - Don't scrape all sources at once
   - Wait for quota reset between large batches

2. **Reduce Token Usage**
   - Current prompt is optimized but could be shorter
   - Article content is limited to 50,000 characters (already implemented)
   - Output is limited to 2,048 tokens (already implemented)

3. **Batch Processing**
   - Scrape during off-peak hours
   - Process smaller batches (5-10 pages at a time)
   - Use daily automatic scraping (3 pages = ~15 articles)

4. **Upgrade When Needed**
   - If processing >200 articles/day regularly
   - Paid tier: $0.0014/article is very affordable
   - $1.40 for 1,000 articles is reasonable

---

## 📝 Current Settings

**Rate Limiting:**
- 1 second delay between API calls
- Prevents hitting per-minute limits

**First-Time Scrape:**
- Reduced from 100 pages → 20 pages
- Prevents quota exhaustion

**Daily Scrape:**
- 3 pages max (~15-30 articles)
- Well within free tier limits

**Content Limits:**
- Article content: 50,000 characters max
- Output tokens: 2,048 max
- Optimized for cost efficiency

---

## 🎯 Summary

**Cost Per Article:**
- **~$0.0014 USD** (less than 1 cent per article)
- Very affordable even at scale

**Why Quota Error Persists:**
- It's historical data in the database
- Shows the last failed scraping attempt
- Will clear when next successful scrape runs

**Recommendation:**
- Free tier is fine for daily scraping (15-30 articles/day)
- Upgrade to paid tier if you need >200 articles/day
- Cost is minimal: ~$1.26/month for daily scraping

