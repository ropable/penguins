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

## Installation

Dependencies for this project are managed using [uv](https://docs.astral.sh/uv/).
With uv installed, change into the project directory and run:

    uv sync

Activate the virtualenv like so:

    source .venv/bin/activate

To run Python commands in the activated virtualenv, thereafter run them like so:

    python manage.py

Manage new or updated project dependencies with uv also, like so:

    uv add newpackage==1.0

## Environment variables

This project uses **python-dotenv** to set environment variables (in a `.env` file).
The following variables are required for the project to run:

    DATABASE_URL=postgis://USER:PASSWORD@HOST:PORT/DATABASE_NAME
    SECRET_KEY=ThisIsASecretKey
    GEOSERVER_URL=https://geoserver.url/geoserver
    LAYER_NAME=namespace:layer

## Video uploads

Captured videos are uploaded to Azure container storage as blobs. To serve videos,
account credentials and the container name should be provided as environment variables
in the same `.env` file as follows:

    AZURE_ACCOUNT_NAME=name
    AZURE_ACCOUNT_KEY=key
    AZURE_CONTAINER=container_name

## Running

Use `runserver` to run a local copy of the application:

    python manage.py runserver 0:8080

Run console commands manually:

    python manage.py shell_plus

## Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/penguins .

## Pre-commit hooks

This project includes the following pre-commit hooks:

- TruffleHog: <https://docs.trufflesecurity.com/docs/scanning-git/precommit-hooks/>

Pre-commit hooks may have additional system dependencies to run. Optionally
install pre-commit hooks locally like so:

    pre-commit install

Reference: <https://pre-commit.com/>
