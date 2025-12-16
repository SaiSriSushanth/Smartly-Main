#!/bin/sh

# Run migrations
python manage.py migrate

# Execute the passed command (e.g., celery) or default to gunicorn if no args
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    exec gunicorn --bind 0.0.0.0:8000 smartly.wsgi:application
fi
