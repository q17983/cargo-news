# ✅ Root Directory - Exact Value

## Correct Value

```
frontend
```

**NO trailing slash!**

---

## ❌ Wrong Values

- `frontend/` ❌ (with trailing slash)
- `/frontend` ❌ (with leading slash)
- `./frontend` ❌ (with dot-slash)
- `/frontend/` ❌ (both slashes)

---

## ✅ How to Set in Railway

1. Go to **Settings** → **Root Directory**
2. Type exactly: `frontend`
3. **Do NOT add** `/` at the end
4. Click **Save**

---

## Verification

After setting, the field should show:
```
Root Directory: frontend
```

**NOT:**
```
Root Directory: frontend/
```

---

## Why This Matters

Railway interprets:
- `frontend` = relative path to `frontend/` directory ✅
- `frontend/` = might be interpreted as a file, not directory ❌

---

## Final Answer

**Use: `frontend` (no slash, no leading slash, just the directory name)**

