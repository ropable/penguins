FROM python:3.7.17-slim-buster as builder_base_penguins
MAINTAINER asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source https://github.com/dbca-wa/penguins

WORKDIR /app
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y libmagic-dev gcc binutils gdal-bin proj-bin python3-dev libpq-dev gzip curl \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip

# Install Python libs using poetry.
FROM builder_base_penguins as python_libs_penguins
WORKDIR /app
ENV POETRY_VERSION=1.2.2
RUN pip install "poetry==$POETRY_VERSION"
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Install the project.
FROM python_libs_penguins
COPY gunicorn.py manage.py ./
COPY observations ./observations
COPY penguins ./penguins
RUN python manage.py collectstatic --noinput

# Run the application as the www-data user.
USER www-data
EXPOSE 8080
CMD ["gunicorn", "penguins.wsgi", "--config", "gunicorn.py"]
