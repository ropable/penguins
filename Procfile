web: python manage.py collectstatic --noinput; python manage.py compress; python manage.py run_gunicorn -w 3 -b 0.0.0.0:$PORT
worker: celery worker -A penguins --loglevel=INFO
