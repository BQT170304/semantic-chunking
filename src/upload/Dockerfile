FROM python:3.11-slim

# Install system dependencies for OpenCV, Tesseract, and other libraries
RUN apt-get update && apt-get install -y \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-vie \
    # PDF processing
    poppler-utils \
    # General utilities
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set Python path to include both /app and /app/src
ENV PYTHONPATH="/app:/app/src"

# Expose port
EXPOSE 8000
