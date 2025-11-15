#!/bin/sh
# Entrypoint script for Railway deployment
# Expands PORT environment variable properly

# Debug: Print environment variables
echo "=== Environment Debug ==="
echo "PORT=${PORT}"
echo "PWD=$(pwd)"
echo "========================"

# Get PORT from environment, default to 8000
PORT_VALUE=${PORT:-8000}

# Ensure PORT_VALUE is a number
if ! echo "$PORT_VALUE" | grep -qE '^[0-9]+$'; then
    echo "ERROR: PORT is not a valid number: '$PORT_VALUE'"
    echo "Falling back to port 8000"
    PORT_VALUE=8000
fi

echo "Starting uvicorn on port: $PORT_VALUE"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT_VALUE"

