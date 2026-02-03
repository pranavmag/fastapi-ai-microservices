# ==================================
# STAGE 1: The Builder
# ==================================
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .

# Install packages normally (not with --target)
RUN pip install -r requirements.txt

# ==================================
# STAGE 2: The Runtime
# ==================================
FROM python:3.13-slim

WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy installed packages from standard Python location
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy executables (uvicorn, etc.) from standard bin location
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Environment variables
ENV PORT=8000

# Fix permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs').getcode() == 200" || exit 1

# Startup command
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
