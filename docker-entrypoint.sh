#!/bin/bash

echo "Make database migrations"
python3 manage.py makemigrations

echo "Applying database migrations..."
python3 manage.py migrate

echo "Make application migrations"
python3 manage.py makemigrations catalog

echo "Applying application migrations..."
python3 manage.py migrate catalog

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
gunicorn diaplus.wsgi:application --bind 0.0.0.0:8000 --workers 1
