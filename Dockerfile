FROM python:2.7.18-slim-buster
MAINTAINER asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source https://github.com/dbca-wa/penguins

WORKDIR /app
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y wget gcc gdal-bin libsasl2-dev python-dev libssl-dev libxml2-dev libxslt1-dev \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip
COPY manage.py requirements.txt ./
RUN pip install --no-cache-dir --no-warn-conflicts -r requirements.txt \
  # Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
  # Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
  && sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/site-packages/django/contrib/gis/geos/libgeos.py

# Added in Django 1.7, needed by azure_storage module.
COPY utils/deconstruct.py /usr/local/lib/python2.7/site-packages/django/utils/
COPY observations ./observations
COPY penguins ./penguins
COPY utils ./utils
RUN python manage.py collectstatic --noinput

# Run the application as the www-data user.
USER www-data
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
EXPOSE 8080
CMD ["python", "manage.py", "runwsgiserver", "host=0.0.0.0", "port=8080", "staticserve=collectstatic"]
