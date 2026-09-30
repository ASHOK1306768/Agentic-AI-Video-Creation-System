FROM python:3.10-slim-bookworm

WORKDIR /app

# Install system dependencies with retry logic
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ /app/

# Create output directories
RUN mkdir -p /app/outputs /files /app/outputs/visuals /app/outputs/audio /app/outputs/subtitles /app/outputs/videos

EXPOSE 5000

CMD ["python", "app.py"]
