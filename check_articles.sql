-- SQL Queries to Check Articles in Supabase
-- Run these in Supabase SQL Editor

-- ============================================
-- 1. COUNT ARTICLES BY SOURCE
-- ============================================
-- This shows how many articles each source has
SELECT 
    ns.name AS source_name,
    ns.url AS source_url,
    COUNT(a.id) AS article_count
FROM news_sources ns
LEFT JOIN articles a ON a.source_id = ns.id
GROUP BY ns.id, ns.name, ns.url
ORDER BY article_count DESC;

-- ============================================
-- 2. DETAILED ARTICLE COUNT WITH SOURCE INFO
-- ============================================
-- More detailed breakdown
SELECT 
    ns.id AS source_id,
    ns.name AS source_name,
    ns.url AS source_url,
    COUNT(a.id) AS total_articles,
    COUNT(CASE WHEN a.published_date IS NOT NULL THEN 1 END) AS articles_with_date,
    MIN(a.created_at) AS oldest_article,
    MAX(a.created_at) AS newest_article
FROM news_sources ns
LEFT JOIN articles a ON a.source_id = ns.id
GROUP BY ns.id, ns.name, ns.url
ORDER BY total_articles DESC;

-- ============================================
-- 3. LIST ALL ARTICLES BY SOURCE (with pagination)
-- ============================================
-- List first 100 articles from each source
SELECT 
    ns.name AS source_name,
    a.id,
    a.title,
    a.url,
    a.published_date,
    a.created_at,
    array_length(a.tags, 1) AS tag_count
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
ORDER BY ns.name, a.created_at DESC
LIMIT 200;

-- ============================================
-- 4. CHECK AIR CARGO NEWS ARTICLES SPECIFICALLY
-- ============================================
-- Get all Air Cargo News articles
SELECT 
    a.id,
    a.title,
    a.url,
    a.published_date,
    a.created_at,
    a.scraped_at
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE ns.url LIKE '%aircargonews.net%'
ORDER BY a.created_at DESC;

-- ============================================
-- 5. COUNT AIR CARGO NEWS ARTICLES
-- ============================================
-- Exact count for Air Cargo News
SELECT 
    COUNT(*) AS total_aircargonews_articles
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE ns.url LIKE '%aircargonews.net%';

-- ============================================
-- 6. CHECK STAT TIMES ARTICLES
-- ============================================
-- Get all STAT Times articles
SELECT 
    a.id,
    a.title,
    a.url,
    a.published_date,
    a.created_at
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE ns.url LIKE '%stattimes.com%'
ORDER BY a.created_at DESC;

-- ============================================
-- 7. COUNT STAT TIMES ARTICLES
-- ============================================
-- Exact count for STAT Times
SELECT 
    COUNT(*) AS total_stattimes_articles
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE ns.url LIKE '%stattimes.com%';

-- ============================================
-- 8. CHECK AIR CARGO WEEK ARTICLES
-- ============================================
-- Get all Air Cargo Week articles
SELECT 
    a.id,
    a.title,
    a.url,
    a.published_date,
    a.created_at
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE ns.url LIKE '%aircargoweek.com%'
ORDER BY a.created_at DESC;

-- ============================================
-- 9. CHECK RECENT SCRAPING LOGS
-- ============================================
-- See what the scraping logs say
SELECT 
    sl.id,
    sl.created_at,
    ns.name AS source_name,
    sl.status,
    sl.articles_found,
    sl.error_message
FROM scraping_logs sl
JOIN news_sources ns ON sl.source_id = ns.id
ORDER BY sl.created_at DESC
LIMIT 10;

-- ============================================
-- 10. CHECK FOR DUPLICATE ARTICLES (by URL)
-- ============================================
-- Find any duplicate URLs (shouldn't happen, but let's check)
SELECT 
    url,
    COUNT(*) AS duplicate_count,
    array_agg(id) AS article_ids,
    array_agg(source_id) AS source_ids
FROM articles
GROUP BY url
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- ============================================
-- 11. CHECK ARTICLES CREATED TODAY
-- ============================================
-- See articles created in the last 24 hours
SELECT 
    ns.name AS source_name,
    COUNT(*) AS articles_today,
    MIN(a.created_at) AS first_article,
    MAX(a.created_at) AS last_article
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE a.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY ns.name
ORDER BY articles_today DESC;

-- ============================================
-- 11B. TOTAL ARTICLES (ALL TIME) BY SOURCE
-- ============================================
-- See total articles count for each source (not just today)
SELECT 
    ns.name AS source_name,
    ns.url AS source_url,
    COUNT(*) AS total_articles_all_time,
    COUNT(CASE WHEN a.created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) AS articles_today,
    MIN(a.created_at) AS oldest_article,
    MAX(a.created_at) AS newest_article
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
GROUP BY ns.id, ns.name, ns.url
ORDER BY total_articles_all_time DESC;

-- ============================================
-- 12. CHECK FOR MISSING DATA
-- ============================================
-- Find articles with missing content or summary
SELECT 
    ns.name AS source_name,
    COUNT(*) AS articles_with_missing_data
FROM articles a
JOIN news_sources ns ON a.source_id = ns.id
WHERE a.content IS NULL 
   OR a.content = '' 
   OR a.summary IS NULL 
   OR a.summary = ''
GROUP BY ns.name;

