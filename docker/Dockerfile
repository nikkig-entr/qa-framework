# Multi-stage build for QA Framework
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Playwright
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -e ".[dev]"

# Install Playwright browsers
RUN playwright install --with-deps chromium firefox webkit

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 qa && chown -R qa:qa /app
USER qa

# Default command
ENTRYPOINT ["pytest"]
CMD ["tests", "-v", "--tb=short", "-n", "auto"]