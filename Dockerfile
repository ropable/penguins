FROM python:2.7.15-slim-jessie
MAINTAINER asi@dbca.wa.gov.au

WORKDIR /app
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y wget git gcc gdal-bin mercurial libsasl2-dev python-dev libldap2-dev libssl-dev libxml2-dev libxslt1-dev \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip
COPY manage.py Procfile requirements.txt ./
COPY ldap_email_auth ./ldap_email_auth
COPY observations ./observations
COPY penguins ./penguins
COPY storages ./storages
COPY utils ./utils
RUN pip install --no-cache-dir -r requirements.txt \
  && python manage.py collectstatic --noinput

HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
EXPOSE 8080
CMD ["honcho", "start"]
