# 🚀 Quick Reference - Current System State

## ✅ System Status: **WORKING**

All systems operational. Deployed on Railway.

---

## 🔑 Key Files

### **Backend**
- `Dockerfile` - Custom Dockerfile with Playwright dependencies
- `start_server.py` - Entrypoint script (reads PORT env var)
- `railway.json` - Railway config (DOCKERFILE builder)
- `scrape_aircargoweek.py` - Railway-compatible scraper script

### **Frontend**
- `frontend/Dockerfile` - Next.js Dockerfile
- `frontend/railway.json` - Railway config

---

## 🌐 URLs

- **Backend API**: `https://web-production-1349.up.railway.app` (or your Railway domain)
- **Frontend**: Your Railway frontend domain

---

## 🔧 Environment Variables

### **Backend (Railway)**
```
SUPABASE_URL=...
SUPABASE_KEY=...
OPENAI_API_KEY=...
SCRAPING_DELAY_SECONDS=2
MAX_RETRIES=3
PORT=8000  # Railway sets automatically
```

### **Frontend (Railway)**
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
PORT=8080  # Railway sets automatically
```

---

## ✅ Working Features

- ✅ All 3 scrapers (Air Cargo News, Air Cargo Week, STAT Times)
- ✅ Web UI with source management
- ✅ Manual scraping (individual + "Scrape All")
- ✅ Real-time status updates
- ✅ Stop scraping functionality
- ✅ Article viewing and filtering
- ✅ Bookmarks
- ✅ Daily automatic scraping (00:00 UTC)

---

## 🐛 Common Issues & Fixes

### **Backend won't start**
- Check `start_server.py` is executable
- Verify PORT env var is set
- Check Dockerfile builds successfully

### **Scraper fails**
- Check Playwright dependencies installed
- Verify API keys
- Check network/IP blocking
- Review logs in Supabase

### **Frontend won't load**
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running
- Check Railway domain config

---

## 📝 Important Notes

1. **Railway Detection**: Scripts auto-detect Railway/Docker and skip venv checks
2. **PORT Variable**: Always use `start_server.py` - don't hardcode ports
3. **Playwright**: Air Cargo Week uses subprocess for compatibility
4. **Rate Limiting**: OpenAI API limited to 1 req/sec
5. **Page Limits**: First-time scrape = 5 pages, daily = 5 pages

---

## 🎯 Next Development

See `CHECKPOINT_2025-11-15.md` for detailed next steps.

---

**Last Updated**: November 15, 2025

