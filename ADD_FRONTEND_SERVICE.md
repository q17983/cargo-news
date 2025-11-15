# 🎨 How to Add Frontend Service in Railway

## ✅ Your Backend is Working!

**Backend URL**: https://web-production-1349.up.railway.app/

## 📍 Where to Find "+ New Service"

### Step 1: Go to Your Project

1. In Railway Dashboard, click on your **project name** (the one with your backend)
2. You should see your backend service listed

### Step 2: Find the "+ New" Button

The button location depends on Railway's UI, but it's usually:

**Option A: Top Right Corner**
- Look at the **top right** of your project page
- You should see a **"+ New"** or **"+ Service"** button
- Click it

**Option B: Next to Your Service**
- Look **next to your backend service** (on the right side)
- There might be a **"+"** icon or **"Add Service"** button

**Option C: In the Services List**
- If you see a list of services
- There might be a **"New Service"** button at the top or bottom

### Step 3: Select GitHub Repo

1. After clicking "+ New", you'll see options:
   - **"GitHub Repo"** ← Select this
   - Or "Empty Service"
   - Or "Template"

2. Select **"GitHub Repo"**

3. Railway will show your repositories
4. Select: **q17983/cargo-news**

5. Click **"Deploy"** or **"Add"**

### Step 4: Configure Frontend

Once the service is added:

1. **Click on the new service** (it will have a name like "cargo-news" or similar)

2. **Go to Settings Tab**
   - Click **"Settings"** in the service menu

3. **Set Root Directory**
   - Find **"Root Directory"** field
   - Set it to: `frontend`
   - Click **"Save"**

4. **Set Environment Variable**
   - Go to **"Variables"** tab
   - Click **"+ New Variable"**
   - Add:
     ```
     Variable Name: NEXT_PUBLIC_API_URL
     Value: https://web-production-1349.up.railway.app
     ```
   - Click **"Save"**

5. **Wait for Deployment**
   - Railway will automatically rebuild
   - Check "Deployments" tab for progress
   - Takes 3-5 minutes

### Step 5: Get Frontend URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Copy the URL

---

## 🆘 Still Can't Find It?

### Alternative Method: Via Project Settings

1. Click on your **project name** (not the service)
2. Look for **"Services"** tab or section
3. There should be a way to add a new service there

### Check Your View

Make sure you're looking at:
- ✅ **Project view** (shows your services)
- ❌ NOT the main dashboard (shows all projects)

---

## 📸 What You Should See

**In Project View:**
```
┌─────────────────────────────────────┐
│  Your Project Name                  │
│  ┌───────────────────────────────┐  │
│  │ Backend Service (running)     │  │
│  └───────────────────────────────┘  │
│                                      │
│  [+ New] ← Click this button        │
└─────────────────────────────────────┘
```

---

## 💡 Quick Checklist

- [ ] Backend URL confirmed: https://web-production-1349.up.railway.app/
- [ ] Found "+ New" or "+ Service" button
- [ ] Selected "GitHub Repo"
- [ ] Selected q17983/cargo-news
- [ ] Service added
- [ ] Set Root Directory to `frontend`
- [ ] Set `NEXT_PUBLIC_API_URL` to backend URL
- [ ] Frontend deployed
- [ ] Frontend URL obtained

---

## 🆘 Need More Help?

If you still can't find it, try:
1. **Refresh the page**
2. **Check if you're in the right project**
3. **Look for any "+" icons anywhere on the page**
4. **Take a screenshot** and I can help identify where it is

The button is definitely there - Railway always allows adding multiple services to a project!

