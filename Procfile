web: python manage.py collectstatic --noinput; python manage.py compress; python manage.py run_gunicorn -w 3 -b 0.0.0.0:$PORT
beat: celery beat -A penguins --loglevel=INFO
worker: celery worker -A penguins --loglevel=INFO
