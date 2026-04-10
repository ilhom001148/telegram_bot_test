# Stage 1: Build the React Admin Panel
FROM node:18-alpine AS builder

WORKDIR /app/admin-panel
# Copy package files separately to leverage Docker cache
COPY admin-panel/package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY admin-panel/ ./
RUN npm run build

# Stage 2: Final Runtime Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for psycopg and other builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application
COPY . .

# Copy built admin panel from the builder stage
# This replaces any local 'dist' folder
COPY --from=builder /app/admin-panel/dist /app/admin-panel/dist

# The default port for Render is 10000, but we use ${PORT} from env
EXPOSE 10000

# Start command
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
