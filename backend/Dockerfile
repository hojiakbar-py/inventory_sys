# Backend Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Collect static files (may fail without DB - that's ok)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "inventory_system.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
