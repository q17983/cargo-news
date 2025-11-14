# Webpage vs Standalone Script - IP Address & Execution Differences

## 🌐 IP Address Used

### Both Use the Same IP Address!

**When scraping from webpage:**
- Uses your **server's public IP address** (where FastAPI is running)
- Current IP: `103.219.21.17` (your server's IP)
- The website sees requests coming from this IP

**When scraping from standalone script:**
- Uses your **computer's public IP address** (where you run the script)
- If running locally: Your home/office network IP
- If running on server: Same as webpage (server's IP)

**Key Point:** Both methods use the **same IP address** if running on the same machine/network.

## 🔍 Why Standalone Works But Webpage Doesn't

### The Problem: Playwright in Thread Pools

**Standalone Script:**
- Runs in **main Python thread**
- Direct execution, no threading
- Playwright works perfectly ✅

**Webpage Scraping:**
- Runs in **ThreadPoolExecutor** (background thread)
- Playwright has known issues in threads:
  - Can hang during browser launch
  - Signal handling problems
  - Resource isolation issues
  - Process management conflicts

### The Solution: Use ProcessPoolExecutor

I've changed the code to use **ProcessPoolExecutor** instead of **ThreadPoolExecutor**:

**Benefits:**
- ✅ Better process isolation
- ✅ Playwright works correctly in separate processes
- ✅ No hanging issues
- ✅ Same IP address (still uses server's IP)

**Trade-offs:**
- Slightly more memory usage (separate processes)
- Slightly slower startup (process creation)

## 📊 IP Address Details

### How to Check Your IP

**From command line:**
```bash
curl ifconfig.me
```

**From Python:**
```python
import requests
ip = requests.get('https://api.ipify.org').text
print(f"Your IP: {ip}")
```

### Current Setup

- **Server IP**: `103.219.21.17` (where FastAPI runs)
- **Webpage scraping**: Uses server IP
- **Standalone script**: Uses same IP if run on server, or your local IP if run locally

## 🔧 Technical Details

### Execution Flow Comparison

**Standalone:**
```
Python script (main thread)
  → Playwright browser launch
  → Scrape articles
  → Save to database
```

**Webpage (Before Fix):**
```
FastAPI (main thread)
  → BackgroundTasks
  → ThreadPoolExecutor
  → Playwright (in thread) ❌ HANGS
```

**Webpage (After Fix):**
```
FastAPI (main thread)
  → BackgroundTasks
  → ProcessPoolExecutor
  → Playwright (in process) ✅ WORKS
```

## 💡 Important Notes

1. **IP Blocking**: If your IP is blocked, **both methods will fail** (same IP)
2. **VPN/Proxy**: If you use VPN, both will use VPN IP
3. **Different Networks**: If you run standalone on different network, it will use that network's IP

## 🚀 Next Steps

The code has been updated to use `ProcessPoolExecutor`. This should fix the hanging issue while maintaining the same IP address behavior.

