#!/usr/bin/env python3
"""
Start script for Railway deployment.
Reads PORT from environment and starts uvicorn.
"""
import os
import sys

def main():
    # Change to /app directory where the application code is
    os.chdir('/app')
    
    # Add /app to Python path to ensure imports work
    if '/app' not in sys.path:
        sys.path.insert(0, '/app')
    
    # Debug: Print current directory and Python path
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Print first 3 entries
    
    # Check if app.main exists
    try:
        import app.main
        print("✅ Successfully imported app.main")
    except ImportError as e:
        print(f"❌ Failed to import app.main: {e}", file=sys.stderr)
        print(f"Files in /app: {os.listdir('/app')[:10]}", file=sys.stderr)
        sys.exit(1)
    
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

