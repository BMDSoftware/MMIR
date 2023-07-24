#!/bin/bash
nginx && python manage.py makemigrations --noinput && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
gunicorn mmir_gui.wsgi:application --bind 0.0.0.0:5001 --timeout 800

