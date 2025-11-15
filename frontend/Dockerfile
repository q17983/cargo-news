# Dockerfile for Next.js frontend
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
# Copy all source files
COPY . .

# CRITICAL: Pass NEXT_PUBLIC_API_URL as build argument
# Railway environment variables are available during build
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Verify environment variable is available
RUN echo "=== Checking NEXT_PUBLIC_API_URL ===" && \
    if [ -z "$NEXT_PUBLIC_API_URL" ]; then \
      echo "❌ WARNING: NEXT_PUBLIC_API_URL is not set!"; \
    else \
      echo "✅ NEXT_PUBLIC_API_URL is set to: $NEXT_PUBLIC_API_URL"; \
    fi

# Verify files are copied correctly
RUN echo "=== Files in /app/ ===" && ls -la /app/ && \
    echo "=== Checking lib/ ===" && \
    (test -d /app/lib && echo "✅ lib/ directory exists" || echo "❌ lib/ NOT FOUND") && \
    (test -f /app/lib/api.ts && echo "✅ lib/api.ts found" || echo "❌ lib/api.ts NOT FOUND") && \
    echo "=== Searching for api.ts ===" && \
    find /app -name "api.ts" 2>&1 | head -5

# Build Next.js (this is where NEXT_PUBLIC_API_URL gets embedded)
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
# Copy public directory (now exists in source)
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]

