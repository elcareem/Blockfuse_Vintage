# ─────────────────────────────────────────────────────────────────────────────
# Blockfuse Vintage — Multi-stage Dockerfile
# Stage 1: builder  — install dependencies
# Stage 2: production — lean runtime image with non-root user
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools (needed for some C-extension packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install into a dedicated prefix to copy cleanly to production stage
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: Production ──────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Install only the runtime library needed by PyMySQL + Cloudinary (libmagic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create a non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

# Copy application source
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY gunicorn.conf.py .

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Default command — Gunicorn with UvicornWorker
CMD ["gunicorn", "app.main:app", \
     "--config", "gunicorn.conf.py", \
     "-k", "uvicorn.workers.UvicornWorker"]
