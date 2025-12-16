#!/bin/sh

# Run migrations
python manage.py migrate

# Start Celery worker in background (allow root execution)
export C_FORCE_ROOT=1

echo "Checking environment variables..."
if [ -z "$CELERY_BROKER_URL" ]; then
    echo "WARNING: CELERY_BROKER_URL is not set. Celery might fail."
else
    echo "CELERY_BROKER_URL is set."
fi

echo "Starting Celery worker..."
# Limit concurrency to 1 to save memory on free tier
celery -A smartly worker -l info --concurrency 1 &

# Wait a moment to ensure Celery starts
sleep 5

# Execute the passed command (e.g., from Render settings) or default to gunicorn
if [ "$#" -gt 0 ]; then
    echo "Executing passed command: $@"
    exec "$@"
else
    echo "Starting default Gunicorn..."
    # Limit workers to 1 to save memory (critical for free tier)
    # Increase timeout to 120s to prevent startup kills
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 smartly.wsgi:application
fi
