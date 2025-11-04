FROM python:3.10-slim-buster

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Create required directories and set permissions
RUN mkdir -p /app/frontend /app/outputs /app/uploads /app/logs /tmp/matplotlib \
    && chmod -R 777 /app/outputs /app/uploads /app/logs /tmp/matplotlib

# Set Matplotlib config dir to writable location
ENV MPLCONFIGDIR=/tmp/matplotlib

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]