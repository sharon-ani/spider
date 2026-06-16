# SPIDER — Dockerfile
# Multi-stage build for minimal production image

# ─── Stage 1: Builder ────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into a venv
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt \
    && /venv/bin/pip install --no-cache-dir gunicorn psycopg2-binary

# ─── Stage 2: Production ─────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="Sharon"
LABEL description="SPIDER SSH Intelligence Dashboard"
LABEL version="1.0.0"

# Install runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r spider && useradd -r -g spider -d /app spider

WORKDIR /app
RUN chown spider:spider /app

# Copy venv from builder
COPY --from=builder /venv /venv

# Copy application code
COPY --chown=spider:spider . .

# Create log directory
RUN mkdir -p /var/log/spider && chown spider:spider /var/log/spider

# Switch to non-root user
USER spider

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/stats || exit 1

# Environment defaults
ENV FLASK_ENV=production \
    DEMO_MODE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run with gunicorn
CMD ["/venv/bin/gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
