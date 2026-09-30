FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (FFmpeg, graphics libraries for MoviePy, fonts)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create output directories
RUN mkdir -p /app/outputs /files /app/outputs/visuals /app/outputs/audio /app/outputs/subtitles /app/outputs/videos

EXPOSE 5000

# Default command
CMD ["python", "app.py"]
