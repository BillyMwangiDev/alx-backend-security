#!/usr/bin/env bash
set -e

echo "Running migrations..."
python ip_tracking_project/manage.py migrate --no-input

echo "Starting Gunicorn..."
gunicorn --chdir ip_tracking_project wsgi:application
