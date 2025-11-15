# 🚀 Deployment Quick Reference

## ⚡ Quick Checklist

### Before Deploying Frontend

1. ✅ Set `NEXT_PUBLIC_API_URL` in Railway Variables
   - Value: `https://web-production-1349.up.railway.app`
   - No trailing slash, no quotes

2. ✅ Verify Dockerfile has:
   ```dockerfile
   ARG NEXT_PUBLIC_API_URL
   ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
   ```
   (BEFORE `npm run build`)

3. ✅ Push code to GitHub (Railway auto-deploys)

4. ✅ Check build logs for:
   - `✅ NEXT_PUBLIC_API_URL is set to: https://...`

5. ✅ After deploy, hard refresh browser

---

## 🔍 Quick Debug Commands

### Test Backend
```bash
curl https://web-production-1349.up.railway.app/health
```

### Test Frontend API
```bash
curl https://web-production-1349.up.railway.app/api/articles?limit=5
```

### Check Running Tasks
```bash
curl https://web-production-1349.up.railway.app/api/scrape/running
```

---

## 🚨 Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Frontend using localhost | Set `NEXT_PUBLIC_API_URL` in Railway → Redeploy |
| Build fails: Module not found | Check Root Directory = `frontend` (no slash) |
| Port mismatch | Check Target Port in Railway domain settings |
| API key leaked | Generate new key → Update in Railway → Redeploy |

---

## 📍 Key Files

- `frontend/Dockerfile` - Must pass `NEXT_PUBLIC_API_URL` during build
- `frontend/lib/api.ts` - Uses `process.env.NEXT_PUBLIC_API_URL`
- `frontend/railway.json` - Railway config (Dockerfile builder)
- `app/config.py` - Backend config (loads from env vars)

---

**See `DEPLOYMENT_CHECKPOINT.md` for full details.**

