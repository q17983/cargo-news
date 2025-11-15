# 🔌 Set Target Port for Railway Domain

## Quick Answer

**Enter: `3000`**

This is the port your Next.js application is listening on (configured in Dockerfile).

---

## Step-by-Step

1. **In the "Target port" field**, enter: `3000`
2. **Click "Generate Domain"**
3. Railway will create your public URL
4. **Copy the URL** and open it in your browser!

---

## Why Port 3000?

- Your Dockerfile sets `ENV PORT 3000`
- Next.js standalone mode listens on port 3000 by default
- Railway will route external traffic to this port

---

## After Generating

1. **Domain will appear** in the list (e.g., `https://cargo-news-production.up.railway.app`)
2. **Copy the URL**
3. **Open in browser** to access your website!

---

## ✅ Quick Checklist

- [ ] Enter `3000` in Target port field
- [ ] Click "Generate Domain"
- [ ] Domain appears in list
- [ ] Copy URL and test in browser
- [ ] Verify frontend has `NEXT_PUBLIC_API_URL` set to backend URL

