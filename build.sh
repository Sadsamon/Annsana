#!/usr/bin/env bash
# Render calls this as the build command.
set -e

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
