# Stage 1: Build frontend assets
FROM node:lts-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies exactly as locked
RUN npm ci

# Copy source files
COPY assets ./assets
COPY vite.config.js ./

# Build assets
RUN npm run build

# Stage 2: Shared Python base (runtime dependencies only)
FROM python:3.14-slim AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (psycopg ships binary wheels, so no compiler or libpq-dev)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Development image (used by docker-compose; code is bind-mounted)
FROM base AS dev

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

EXPOSE 5001

CMD ["python", "run.py"]

# Stage 4: Production image (default target, must stay last)
FROM base AS production

# Copy application code
COPY . .

# Copy built frontend assets from frontend-builder stage
COPY --from=frontend-builder /app/static/dist ./static/dist

# Expose port (run.py listens on FLASK_RUN_PORT, default 5001)
EXPOSE 5001

# Run the application
CMD ["python", "run.py"]
