# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for matplotlib & gcc
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Ensure required directories exist
RUN mkdir -p /app/frontend /app/outputs /app/uploads

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]