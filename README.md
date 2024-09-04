# Penguin Observations Application

The Penguins Observations application is a Django application developed
by the Western Australian Department of Parks and Wildlife. It is used
by Department staff and members of the public to record observations of
Little Penguin visits to Penguin Island in WA. Observation records and
captured by video cameras on the island, and the application is used to
review and count penguin visits.

The Penguins Observations application was developed using the Django web
framework, the Python programming language and PostgreSQL database. The
application source code is freely available according to the terms of
the attached licence.

# Installation

This project requires a Python 2.7.* environment to run. For development, set up
a virtual environment running a local copy of Python and then install the
project dependencies using `pip`:

    pip install -r requirements.txt

# Environment variables

This project uses environment variables (in a `.env` file) to define application settings.
Required settings are as follows:

    DATABASE_URL=postgis://USER:PASSWORD@HOST:PORT/DATABASE_NAME
    SECRET_KEY=ThisIsASecretKey
    GEOSERVER_URL=https://geoserver.url/geoserver
    LAYER_NAME=namespace:layer

# Video uploads

Captured videos are uploaded to Azure container storage as blobs. To serve videos,
account credentials and the container name should be provided as environment variables
in the same `.env` file as follows:

    AZURE_ACCOUNT_NAME=name
    AZURE_ACCOUNT_KEY=key
    AZURE_CONTAINER=container_name

# Running

Use `runserver` to run a local copy of the application:

    python manage.py runserver 0:8080

Run console commands manually:

    python manage.py shell_plus

# Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/penguins .

# Pre-commit hooks

This project includes pre-commit hooks as a means of preventing sensitive information
from being committed into the repository using [TruffleHog](https://docs.trufflesecurity.com/docs/scanning-git/precommit-hooks/).

If TruffleHog is available in your development environment, install pre-commit hooks
locally like so (this is optional):

    pre-commit install --allow-missing-config

Reference: <https://pre-commit.com/>
