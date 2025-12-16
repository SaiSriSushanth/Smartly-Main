#!/bin/sh

# Run migrations
python manage.py migrate

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:8000 smartly.wsgi:application
