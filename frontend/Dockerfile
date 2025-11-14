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

# Verify files are copied correctly
RUN echo "=== Files in /app/ ===" && ls -la /app/ && \
    echo "=== Checking lib/ ===" && \
    (test -d /app/lib && echo "✅ lib/ directory exists" || echo "❌ lib/ NOT FOUND") && \
    (test -f /app/lib/api.ts && echo "✅ lib/api.ts found" || echo "❌ lib/api.ts NOT FOUND") && \
    echo "=== Searching for api.ts ===" && \
    find /app -name "api.ts" 2>&1 | head -5

# Build Next.js
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]

