#!/bin/bash
python manage.py makemigrations --noinput && python manage.py migrate --noinput && python manage.py runserver 127.0.0.1:5000
