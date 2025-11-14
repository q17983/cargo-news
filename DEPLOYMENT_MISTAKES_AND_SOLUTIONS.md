# Deployment Mistakes and Solutions - Complete Summary

## Overview
This document records all deployment mistakes encountered during Railway deployment and their solutions to prevent future issues.

---

## Critical Mistakes & Solutions

### 1. **Path Alias Resolution (`@/lib/api` not found)**

**Mistake:**
- Used TypeScript path aliases (`@/lib/api`) in Next.js
- Railway build couldn't resolve these aliases
- Error: `Module not found: Can't resolve '@/lib/api'`

**Root Causes:**
- `tsconfig.json` missing `baseUrl` configuration
- `next.config.js` webpack aliases not working in Railway's build environment
- Railway's build context was incorrect (Root Directory setting)

**Solutions Applied:**
1. ✅ Added `"baseUrl": "."` to `tsconfig.json`
2. ✅ Converted all `@/` imports to relative imports (`../lib/api`)
3. ✅ Set Railway Root Directory to `frontend` (no leading slash)
4. ✅ Created `frontend/nixpacks.toml` with `baseDirectory = "frontend"`

**Lesson:** Always use relative imports for production deployments, or ensure build tools properly resolve path aliases.

---

### 2. **Missing `lib/api.ts` File in Git**

**Mistake:**
- `frontend/lib/api.ts` was ignored by `.gitignore`
- File wasn't tracked by Git
- Railway couldn't access the file during build
- Error: `ls: /app/lib/: No such file or directory`

**Root Cause:**
- Root `.gitignore` had patterns that excluded `lib/` directories
- File wasn't committed to Git repository

**Solution:**
1. ✅ Modified `.gitignore` to explicitly unignore `frontend/lib/`
2. ✅ Force-added `frontend/lib/api.ts` to Git
3. ✅ Verified file is tracked: `git ls-files frontend/lib/api.ts`

**Lesson:** Always verify critical files are tracked by Git before deployment. Check `.gitignore` carefully.

---

### 3. **Redundant Docker COPY Command**

**Mistake:**
- Added explicit `COPY lib/* /app/lib/` command in Dockerfile
- This tried to copy to the same location already copied by `COPY . .`
- Error: `cp: 'lib/api.ts' and '/app/lib/api.ts' are the same file`

**Root Cause:**
- Misunderstanding of Docker COPY behavior
- `COPY . .` already copies all files including `lib/`

**Solution:**
1. ✅ Removed redundant copy command
2. ✅ Verified `lib/` is copied by `COPY . .`

**Lesson:** Don't duplicate COPY commands. `COPY . .` copies everything from build context.

---

### 4. **Missing `public` Directory**

**Mistake:**
- Next.js standalone build doesn't include `public/` directory by default
- Dockerfile tried to `COPY --from=builder /app/public ./public`
- Error: `"/app/public": not found`

**Root Cause:**
- No `public/` directory existed in source code
- Next.js standalone mode requires explicit `public/` directory

**Solution:**
1. ✅ Created empty `frontend/public/` directory with `.gitkeep`
2. ✅ Updated Dockerfile to copy `public` directory normally

**Lesson:** Next.js standalone builds require explicit `public/` directory. Always create it even if empty.

---

### 5. **Wrong Start Command in `railway.json`**

**Mistake:**
- `railway.json` had `"startCommand": "npm start"` which runs `next start`
- But Next.js standalone mode requires `node server.js`
- Error: `sh: next: not found` (because `next` isn't installed in standalone build)

**Root Cause:**
- Confusion between Next.js development mode (`next start`) and standalone mode (`node server.js`)
- Railway was using `railway.json` to override Dockerfile CMD

**Solution:**
1. ✅ Changed `railway.json` to use `"startCommand": "node server.js"`
2. ✅ Set builder to `"DOCKERFILE"` to use Dockerfile instead of Nixpacks

**Lesson:** Next.js standalone mode (`output: 'standalone'`) requires `node server.js`, NOT `next start`. The standalone build is self-contained and doesn't include the `next` CLI.

---

## Configuration Files Summary

### ✅ Correct `frontend/railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "node server.js"
  }
}
```

### ✅ Correct `frontend/next.config.js`:
```javascript
{
  output: 'standalone',  // Required for Docker deployment
  // ... other config
}
```

### ✅ Correct `frontend/Dockerfile` Structure:
1. Multi-stage build (deps → builder → runner)
2. Copy `public/` directory
3. Copy `.next/standalone/` to root
4. Copy `.next/static/` for static assets
5. CMD: `["node", "server.js"]`

### ✅ Correct Import Strategy:
- Use relative imports: `../lib/api` instead of `@/lib/api`
- Or ensure path aliases are properly configured for production builds

---

## Railway Settings Checklist

### ✅ Root Directory:
- **Value:** `frontend` (NO leading slash)
- **Location:** Service Settings → Root Directory
- **Why:** Tells Railway where to find the project files

### ✅ Build Command:
- **Value:** (Leave empty - Dockerfile handles it)
- **Or:** Use `railway.json` with `"builder": "DOCKERFILE"`

### ✅ Start Command:
- **Value:** `node server.js` (for standalone mode)
- **Location:** `railway.json` or Service Settings

### ✅ Environment Variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `PORT` - Railway sets this automatically
- `NODE_ENV=production` - Set automatically

---

## Build Process Flow (Correct)

1. **Git Push** → Railway detects changes
2. **Docker Build** (using `frontend/Dockerfile`):
   - Stage 1 (deps): Install npm dependencies
   - Stage 2 (builder): Copy files, build Next.js (`npm run build`)
   - Stage 3 (runner): Copy standalone build, static files, public directory
3. **Container Start**: Run `node server.js` from `.next/standalone/`
4. **Server Running**: Next.js serves on port 3000 (or Railway's PORT)

---

## Common Pitfalls to Avoid

### ❌ DON'T:
1. Use `@/` path aliases without proper build configuration
2. Ignore critical files in `.gitignore`
3. Use `next start` with standalone mode
4. Set Root Directory to `/frontend` (leading slash breaks it)
5. Use Nixpacks when you have a Dockerfile
6. Copy files redundantly in Dockerfile
7. Forget to create `public/` directory

### ✅ DO:
1. Use relative imports for production
2. Verify all files are tracked by Git
3. Use `node server.js` for standalone mode
4. Set Root Directory to `frontend` (no slash)
5. Use Dockerfile for consistent builds
6. Let `COPY . .` handle file copying
7. Always create `public/` directory (even if empty)

---

## Testing Checklist Before Deployment

- [ ] All imports use relative paths (or path aliases are properly configured)
- [ ] `lib/api.ts` exists and is tracked by Git
- [ ] `public/` directory exists (even if empty)
- [ ] `railway.json` uses `node server.js` (not `next start`)
- [ ] `next.config.js` has `output: 'standalone'`
- [ ] Dockerfile copies all necessary files
- [ ] Root Directory is set to `frontend` (no leading slash)
- [ ] Build succeeds locally: `docker build -t test .` in `frontend/` directory
- [ ] Local test: `docker run -p 3000:3000 test` works

---

## Debugging Commands

### Check if file is in Git:
```bash
git ls-files frontend/lib/api.ts
```

### Test Docker build locally:
```bash
cd frontend
docker build -t cargo-news-frontend .
docker run -p 3000:3000 cargo-news-frontend
```

### Verify Railway settings:
- Check Service Settings → Root Directory
- Check Service Settings → Build Command (should be empty or use Dockerfile)
- Check Service Settings → Start Command (should be `node server.js`)

---

## Final Notes

**Key Principle:** Next.js standalone mode creates a self-contained build that doesn't require the `next` CLI. Always use `node server.js` to start it.

**Git is Critical:** Railway builds from Git. If a file isn't in Git, Railway can't access it.

**Dockerfile is Source of Truth:** When using Dockerfile, Railway should use it for building. Don't mix Nixpacks and Dockerfile configurations.

**Test Locally First:** Always test Docker builds locally before pushing to Railway.

---

## Version History

- **2025-11-14**: Initial document created after 15+ deployment attempts
- Documented all mistakes and solutions for future reference

