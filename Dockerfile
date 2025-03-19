FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV PORT=8080

# Install system dependencies, including curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev curl net-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose the port
EXPOSE 8080

# Start Gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "ngram_app.app:server"]
