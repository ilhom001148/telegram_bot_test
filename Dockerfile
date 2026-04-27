# Stage 1: Build the React Admin Panel
FROM node:20-alpine AS build-stage
WORKDIR /app/admin-panel
COPY admin-panel/package*.json ./
RUN npm install
COPY admin-panel/ ./
RUN npm run build

# Stage 2: Final Runtime Image
FROM python:3.11-slim
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tashkent

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Copy the built React app from stage 1
COPY --from=build-stage /app/admin-panel/dist /app/admin-panel/dist

# Start command
# Render provides the PORT environment variable. We default to 10000 if not provided.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
