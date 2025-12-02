FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for MySQL client
# Note: This requires network access during build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY dadgan_project ./dadgan_project
COPY lawfirm ./lawfirm
COPY templates ./templates
COPY static ./static
COPY manage.py ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install django gunicorn mysqlclient Pillow whitenoise

# Create static files directory
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
ENV DJANGO_SETTINGS_MODULE=dadgan_project.settings
RUN python manage.py collectstatic --noinput --clear || true

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:80/', timeout=2)" || exit 1

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "dadgan_project.wsgi:application"]
