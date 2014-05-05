#!/usr/bin/env bash

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY='IT REALLY DOESNT MATTER FOR THIS PURPOSE'
export DATABASE_URL=$1
#python manage.py syncdb --no-input
#python manage.py migrate --noinput
python manage.py jenkins
