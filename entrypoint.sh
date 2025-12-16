#!/bin/sh

# Run migrations
python manage.py migrate

# Execute the passed command (e.g., celery) or default to gunicorn if no args
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    # Start Celery worker in background
    celery -A smartly worker -l info &
    
    # Start Gunicorn
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} smartly.wsgi:application
fi


