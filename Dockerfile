# Stage 1: Build frontend assets
FROM node:lts-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock* ./

# Install dependencies with Yarn
RUN corepack enable && \
    yarn install --frozen-lockfile

# Copy source files
COPY assets ./assets
COPY vite.config.js ./

# Build assets
RUN yarn build

# Stage 2: Python application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend assets from frontend-builder stage
COPY --from=frontend-builder /app/static/dist ./static/dist

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]