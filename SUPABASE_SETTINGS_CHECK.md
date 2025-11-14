# Supabase Settings Verification

## Required Environment Variables

Make sure your `.env` file (or Railway environment variables) contains:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Optional
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
PORT=8000
```

## How to Get Supabase Credentials

1. **Go to Supabase Dashboard**: https://app.supabase.com
2. **Select your project**
3. **Go to Settings → API**
4. **Copy the following**:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon/public key** → Use as `SUPABASE_KEY` (NOT the service_role key)

## Database Tables Required

Run these SQL scripts in Supabase SQL Editor:

1. **`database_schema.sql`** - Main tables (news_sources, articles, scraping_logs)
2. **`add_bookmarks_table.sql`** - Bookmarks table

## Row Level Security (RLS) Policies

All tables should have RLS enabled with "Allow all operations" policy:

```sql
-- Example for articles table
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations" ON articles
    FOR ALL USING (true) WITH CHECK (true);
```

## Verification Checklist

- [ ] `SUPABASE_URL` is set correctly (should start with `https://`)
- [ ] `SUPABASE_KEY` is the anon/public key (not service_role)
- [ ] All database tables exist (news_sources, articles, scraping_logs, bookmarks)
- [ ] RLS policies are created for all tables
- [ ] Can connect to Supabase (test with `/health` endpoint)
- [ ] Can create sources (test via API or frontend)
- [ ] Can fetch articles (test via API or frontend)

## Testing Connection

Test your Supabase connection:

```bash
# Check if backend can connect
curl http://localhost:8000/health

# Test API endpoints
curl http://localhost:8000/api/sources
curl http://localhost:8000/api/articles?limit=10
```

## Common Issues

1. **"new row violates row-level security policy"**
   - Solution: Run RLS policies from `database_schema.sql`

2. **"Invalid API key"**
   - Solution: Check you're using the anon/public key, not service_role

3. **"Connection refused"**
   - Solution: Verify `SUPABASE_URL` is correct and project is active

4. **"Table does not exist"**
   - Solution: Run the SQL schema scripts in Supabase SQL Editor

