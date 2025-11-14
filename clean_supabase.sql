-- Clean Supabase Data Script
-- Run this in Supabase SQL Editor to delete all data

-- Delete in correct order (respecting foreign key constraints)
DELETE FROM bookmarks;
DELETE FROM articles;
DELETE FROM scraping_logs;
DELETE FROM news_sources;

-- Optional: Reset auto-increment sequences (for clean IDs)
-- Uncomment if you want to reset ID counters
-- ALTER SEQUENCE IF EXISTS news_sources_id_seq RESTART WITH 1;

-- Verify deletion
SELECT 
    (SELECT COUNT(*) FROM bookmarks) as bookmarks_count,
    (SELECT COUNT(*) FROM articles) as articles_count,
    (SELECT COUNT(*) FROM scraping_logs) as logs_count,
    (SELECT COUNT(*) FROM news_sources) as sources_count;

