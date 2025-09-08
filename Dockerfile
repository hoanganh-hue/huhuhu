# Multi-stage Dockerfile for Tools Data BHXH

# Stage 1: Build stage
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json files and install Node.js dependencies
COPY cccd/package*.json ./cccd/
COPY check-cccd/package*.json ./check-cccd/
COPY bhxh-tool-enhanced-python/package*.json ./bhxh-tool-enhanced-python/

RUN cd cccd && npm ci --only=production && cd .. \
    && cd check-cccd && npm ci --only=production && cd .. \
    && cd bhxh-tool-enhanced-python && npm ci --only=production && cd ..

# Stage 2: Production stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy Node.js dependencies from builder stage
COPY --from=builder /app/cccd/node_modules ./cccd/node_modules
COPY --from=builder /app/check-cccd/node_modules ./check-cccd/node_modules
COPY --from=builder /app/bhxh-tool-enhanced-python/node_modules ./bhxh-tool-enhanced-python/node_modules

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs output data

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8080 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "main.py"]