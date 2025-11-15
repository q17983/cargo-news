# Dockerfile for FastAPI backend with Playwright
FROM python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser
RUN playwright install chromium

# Copy application code
COPY . .

# Copy and set up entrypoint scripts
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY start_server.py /start_server.py
RUN chmod +x /start_server.py && \
    python3 -c "import sys; print(f'Python path: {sys.executable}')" && \
    head -1 /start_server.py

# Set PORT environment variable (Railway will override this)
ENV PORT=8000

# Expose port (Railway will map to PORT env var)
EXPOSE 8000

# Use Python script as primary entrypoint (more reliable than shell script)
# Falls back to shell script if Python fails
ENTRYPOINT ["/start_server.py"]

