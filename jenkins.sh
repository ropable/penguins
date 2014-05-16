#!/usr/bin/env bash
source .env
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py syncdb --no-input
python manage.py migrate --no-input
python manage.py jenkins
