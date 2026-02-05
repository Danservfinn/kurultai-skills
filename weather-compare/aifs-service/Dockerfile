FROM python:3.11-slim

# Install system dependencies for ecCodes (GRIB2 support)
RUN apt-get update && apt-get install -y \
    libeccodes0 \
    libeccodes-tools \
    libeccodes-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /tmp/aifs_data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AIFS_DATA_DIR=/tmp/aifs_data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
