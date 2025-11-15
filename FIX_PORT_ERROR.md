# 🔧 Fix: "$PORT is not a valid integer" Error

## Problem
Railway is showing: `Error: Invalid value for '--port': '$PORT' is not a valid integer`

This means Railway is trying to execute a command with `$PORT` literally, without expanding the environment variable.

## Root Cause
Railway might have a **startCommand** configured in the dashboard that overrides the Dockerfile ENTRYPOINT.

## Solution

### Step 1: Check Railway Dashboard Settings

1. **Go to Railway Dashboard**
2. **Click on your Backend Service**
3. **Go to "Settings" tab**
4. **Look for "Start Command" or "Deploy" section**
5. **If you see a startCommand like:**
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   **DELETE IT or leave it EMPTY**

6. **Save the changes**

### Step 2: Verify railway.json

Make sure `railway.json` does NOT have a `startCommand`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 3: Redeploy

After removing the startCommand from Railway dashboard:
1. **Trigger a new deployment** (push to Git or click "Redeploy" in Railway)
2. **Wait for build to complete**
3. **Check logs** - you should see: `Starting uvicorn on port: <number>`

## How It Works Now

The Dockerfile uses a Python script (`start_server.py`) as the ENTRYPOINT that:
1. Reads `PORT` from environment using `os.environ.get()`
2. Validates it's a number
3. Starts uvicorn with the correct port

This works because Python directly accesses environment variables, no shell expansion needed.

## Verification

After redeploying, check the logs. You should see:
```
Starting uvicorn on port: <actual_port_number>
```

NOT:
```
Error: Invalid value for '--port': '$PORT' is not a valid integer
```

