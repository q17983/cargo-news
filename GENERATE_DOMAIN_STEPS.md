# 🌐 Generate Public Domain on Railway

## Step-by-Step Instructions

### Step 1: Generate Domain

1. **In Railway Dashboard**, you're currently looking at the **Networking** section
2. **Under "Public Networking"**, you'll see a button: **"Generate Domain"**
3. **Click "Generate Domain"**
4. Railway will create a public URL for you, something like:
   ```
   https://cargo-news-production.up.railway.app
   ```
5. **Copy this URL** - this is your website address!

### Step 2: Wait for Domain to Activate

- Railway will automatically configure the domain
- This usually takes 1-2 minutes
- You'll see the domain appear in the list

### Step 3: Access Your Website

1. **Copy the generated URL**
2. **Open it in your browser**
3. **You should see your Cargo News website!**

---

## ⚠️ Important: Set Environment Variable First

Before the website works fully, make sure your **Frontend Service** has the backend URL configured:

1. **Go to your Frontend Service** (not the one you're currently looking at)
2. **Go to "Variables" tab**
3. **Add or verify this variable**:
   ```
   NEXT_PUBLIC_API_URL = https://web-production-1349.up.railway.app
   ```
   (Replace with your actual backend URL)

---

## 🔍 Which Service Are You Looking At?

**Important:** You need to generate domains for **BOTH** services:

1. **Backend Service** - Already has: `https://web-production-1349.up.railway.app`
2. **Frontend Service** - Needs domain generated (this is what you're doing now)

Make sure you're generating the domain for the **Frontend Service** (the Next.js one), not the backend!

---

## ✅ After Generating Domain

Once you have the frontend domain:

1. **Test it**: Open the URL in your browser
2. **Verify backend connection**: Make sure `NEXT_PUBLIC_API_URL` is set correctly
3. **Bookmark it**: This is your website's public address!

---

## 🎯 Quick Checklist

- [ ] Clicked "Generate Domain" button
- [ ] Domain appears in the list (e.g., `https://cargo-news-production.up.railway.app`)
- [ ] Frontend service has `NEXT_PUBLIC_API_URL` variable set to backend URL
- [ ] Can access the domain in browser
- [ ] Website loads successfully

