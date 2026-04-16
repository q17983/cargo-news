# 🔒 API Key Security Guide

## ⚠️ Why Your API Key Was Leaked

**The Problem:** Your OpenAI API key was hardcoded in multiple documentation files (`.md` files) that were committed to GitHub. This made your API key publicly visible, which is why Google detected it as "leaked" and revoked it.

## ✅ How to Prevent API Key Leaks

### 1. **Never Commit API Keys to Git**

❌ **DON'T DO THIS:**
```markdown
# In any .md file
OPENAI_API_KEY=AIzaSyYourActualKeyHere
```

❌ **DON'T DO THIS:**
```python
# In any .py file
API_KEY = "AIzaSyYourActualKeyHere"
```

✅ **DO THIS INSTEAD:**
```markdown
# In documentation files
OPENAI_API_KEY=your_actual_openai_api_key_here
# Or use placeholders like: YOUR_OPENAI_API_KEY_HERE
```

### 2. **Use Environment Variables Only**

✅ **Correct Approach:**
- Store API keys in `.env` file (local development)
- Store API keys in Railway environment variables (production)
- `.env` is already in `.gitignore` ✅

### 3. **What's Already Protected**

✅ **Your `.gitignore` already includes:**
```
.env
.env.local
```

This means `.env` files won't be committed to Git.

### 4. **Best Practices Checklist**

- [x] `.env` is in `.gitignore` ✅
- [x] All hardcoded keys removed from documentation ✅
- [ ] Never commit actual API keys to any file
- [ ] Use placeholders in documentation (`your_actual_openai_api_key_here`)
- [ ] Store real keys only in:
  - Local: `.env` file (not tracked by Git)
  - Production: Railway environment variables

## 🔧 How to Set Up API Keys Safely

### Local Development

1. **Create `.env` file** in project root (if it doesn't exist)
2. **Add your API key:**
   ```bash
   OPENAI_API_KEY=your_actual_key_here
   ```
3. **Verify `.env` is in `.gitignore`** (it already is ✅)
4. **Never commit `.env` to Git**

### Railway (Production)

1. Go to Railway Dashboard → Your Backend Service
2. Click "Variables" tab
3. Add/Update `OPENAI_API_KEY`
4. Set value to your actual API key
5. Railway stores it securely (not in code)

## 🚨 If You Accidentally Commit a Key

1. **Immediately regenerate the API key** at https://aistudio.google.com/apikey
2. **Remove the key from Git history** (if it was committed):
   ```bash
   # Remove from all commits (use with caution!)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Update the key** in Railway and `.env`
4. **Force push** (only if you're sure):
   ```bash
   git push origin --force --all
   ```

## 📋 Quick Reference

| Location | What to Store | Example |
|----------|---------------|---------|
| `.env` file | ✅ Actual API key | `OPENAI_API_KEY=AIzaSy...` |
| Railway Variables | ✅ Actual API key | `OPENAI_API_KEY=AIzaSy...` |
| Documentation (`.md`) | ❌ Placeholder only | `OPENAI_API_KEY=your_key_here` |
| Code (`.py`) | ❌ Never hardcode | Use `settings.openai_api_key` |

## ✅ Current Status

- ✅ All hardcoded API keys removed from documentation
- ✅ `.env` is in `.gitignore`
- ✅ Code uses environment variables correctly
- ⚠️ **Action Required:** Get a new API key and update Railway + `.env`

## 🔑 Getting a New API Key

1. Go to: https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the new key
4. Update:
   - Local `.env` file
   - Railway environment variables
5. **Never commit it to Git!**

---

**Remember:** If you can see an API key in a file that's tracked by Git, so can everyone else on the internet!

