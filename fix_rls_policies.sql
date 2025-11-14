-- Fix Row Level Security Policies
-- Run this in Supabase SQL Editor to allow all operations

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow all operations" ON news_sources;
DROP POLICY IF EXISTS "Allow all operations" ON articles;
DROP POLICY IF EXISTS "Allow all operations" ON scraping_logs;

-- Create policies to allow all operations (for single-user app)
CREATE POLICY "Allow all operations" ON news_sources
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations" ON articles
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations" ON scraping_logs
    FOR ALL USING (true) WITH CHECK (true);

