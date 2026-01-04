# CVE.ICU Docker Container
# Automated CVE data fetching and processing with hourly updates

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UPDATE_INTERVAL=3600 \
    WEB_PORT=8090 \
    TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY build.py .
COPY site_config.json .
COPY data/ ./data/
COPY templates/ ./templates/
COPY web/static/ ./web/static/

# Create directories for volumes
RUN mkdir -p /app/web/data \
    && mkdir -p /app/data/cache \
    && mkdir -p /var/log/cveicu

# Copy entrypoint and scripts
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose web server port
EXPOSE ${WEB_PORT}

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=10m --retries=3 \
    CMD curl -f http://localhost:${WEB_PORT}/ || exit 1

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

