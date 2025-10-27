# Brother Label API - Docker Configuration
# Works with any Python 3.9+ version thanks to bundled fixed brother_ql
# Using Python 3.13 for latest features and security updates

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for USB support)
# RUN apt-get update && apt-get install -y \
#     libusb-1.0-0-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Copy the bundled fixed brother_ql library
COPY brother_ql_fixed/ ./brother_ql_fixed/

# Install Python dependencies (includes our fixed brother_ql)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY brother_ql_handler.py .
COPY printer_manager.py .

# Create config directory
RUN mkdir -p /app/config

# Expose port
EXPOSE 5000

# Environment variables
ENV PORT=5000
ENV DEBUG=False
ENV CONFIG_FILE=/app/config/config.json

# Run the application
CMD ["python", "app.py"]
