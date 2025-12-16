#!/bin/sh

# Run migrations
python manage.py migrate

# Execute the passed command (e.g., celery) or default to gunicorn if no args
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    # Start Celery worker in background (allow root execution)
    export C_FORCE_ROOT=1
    
    echo "Checking environment variables..."
    if [ -z "$CELERY_BROKER_URL" ]; then
        echo "WARNING: CELERY_BROKER_URL is not set. Celery might fail."
    else
    echo "Starting default Gunicorn..."
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} smartly.wsgi:application
fi
