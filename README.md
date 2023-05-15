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

    DATABASE_URL="postgis://USER:PASSWORD@HOST:PORT/DATABASE_NAME"
    SECRET_KEY="ThisIsASecretKey"

# Running

Use `runserver` to run a local copy of the application:

    python manage.py runserver 0:8080

Run console commands manually:

    python manage.py shell_plus

# Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/penguins .
