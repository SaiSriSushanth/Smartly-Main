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
        echo "CELERY_BROKER_URL is set."
    fi
    
    echo "Starting Celery worker..."
    celery -A smartly worker -l info &
    
    # Wait a moment to ensure Celery starts (and log any immediate errors)
    sleep 5
    
    # Start Gunicorn
    echo "Starting Gunicorn..."
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} smartly.wsgi:application

fi
