# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed/threads data/processed/attachments data/indexes runs

# Expose ports
EXPOSE 8000 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENAI_API_KEY=""

# Default command (can be overridden in docker-compose)
CMD ["python", "scripts/run_api.py"]