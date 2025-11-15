#!/usr/bin/env python3
"""
Start script for Railway deployment.
Reads PORT from environment and starts uvicorn.
"""
import os
import sys

def main():
    # Get PORT from environment, default to 8000
    port = os.environ.get('PORT', '8000')
    
    # Validate port is a number
    try:
        port = int(port)
    except ValueError:
        print(f"ERROR: PORT is not a valid number: '{port}'", file=sys.stderr)
        print("Falling back to port 8000", file=sys.stderr)
        port = 8000
    
    print(f"Starting uvicorn on port: {port}")
    
    # Import uvicorn and run
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()

