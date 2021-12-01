Development
***********

Local environment
=================

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^
Backend
"""""""
Requirements when using SQLite database:
::

    pip install -r requirements.txt -r requirements-dev.txt

Requirements when using PostgreSQL database:
::

    pip install -r requirements.txt -r requirements-dev.txt -r requirements-postgres.txt

If You want to develop using other database, please check SQLAlchemy `supported dialects. <https://docs.sqlalchemy.org/en/13/dialects/>`__

Frontend
""""""""
Requirements:
 - Node.js
 - Yarn

To install frontend requirements run:
::

    cd frontend && yarn install

Running application
^^^^^^^^^^^^^^^^^^^

Web Server
""""""""""
Running app with SQLite database:
::

    rfhub2

Running app with PostgreSQL database:
::

    RFHUB_DB_URI=postgresql://postgres:postgres@localhost:5432/postgres rfhub2

| Assuming that DB Server is started on localhost:5432, with postgres as user, password and database name.
| For more details on DB_URI construction please refer to `SQLAlchemy Database URLs documentation. <https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls>`__

CLI
"""
Populating application running on localhost:
::

    rfhub2-cli ../your_repo ../your_other_repo

Populating application running on another host, with non-default credentials:
::

    rfhub2-cli -a http://your_host:8000 -u user -p password ../your_repo ../your_other_repo

Populating app but skipping loading RFWK installed libraries:
::

    rfhub2-cli --no-installed-keywords ../your_repo ../your_other_repo

Preserving already loaded collections and adding new ones:
::

    rfhub2-cli -l append ../your_repo ../your_other_repo

Flushing the database and populating app with collections from provided paths:
::

    rfhub2-cli --load-mode=insert ../your_repo ../your_other_repo

Frontend
""""""""
To run frontend development server execute:
::

    cd frontend && yarn start

To create frontend build run:
::

    yarn build

To create frontend build and add its files to rfhub2 package static files directory execute:
::

    ./build_ui.sh

Running tests
^^^^^^^^^^^^^

Unit tests
""""""""""
To run unit tests simply run:
::

    python -m unittest tests

To run unit tests, collect coverage data and create html report from it run:
::

    python -m coverage run --source rfhub2 -m unittest -b tests && coverage html


Formatting
^^^^^^^^^^
Black is used for code formatting. Checking it is included in CI pipeline. To reformat code after edit, execute:
::

    black -t py36 rfhub2 tests

You can consider adding a git hook or integrating it with your IDE for automated execution.

Database migrations
^^^^^^^^^^^^^^^^^^^
| When you introduce any changes to database schema, you should prepare Alembic revision reflecting these changes.
| To autogenerate revision file, make sure that SQLALCHEMY_DB_URI variable in config points to existing database instance containing database state from previous revision.

To create migration file execute:
::

    PYTHONPATH=. alembic -c rfhub2/alembic.ini revision --autogenerate -m "Your revision name"

Before committing, inspect generated file to make sure that revision contains only relevant changes to the schema.

Creating sphinx documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Application is connected with `Read The Docs <https://readthedocs.org/>`__
which are updated with every release with documentation from `rfhub2/docs/source`.

To create documentation on local environment, run:
::

    cd docs && make html

Documentation will be built in ``rfhub2/docs/_build/html``. Opening ``index.html`` will show its content in browser.

Docker
======

Building application
^^^^^^^^^^^^^^^^^^^^
Building with SQLite database:
::

    docker build -f docker/Dockerfile -t rfhub2 .


Building  with PostgreSQL database:
::

    docker build -f docker/Dockerfile-postgres -t rfhub2:postgres .

Running application
^^^^^^^^^^^^^^^^^^^
To run application with SQlite database execute:
::

    docker run -it -p 8000:8000 rfhub2

To run application with postgreSQL database execute:
::

    docker run -it -p 8000:8000 --network=host -e RFHUB_DB_URI="postgresql://postgres:postgres@localhost:5432/postgres" rfhub2:postgres

| Assuming that DB Server is started on localhost:5432, with postgres as user, password and database name.
| For more details on DB_URI construction please refer to `SQLAlchemy Database URLs documentation. <https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls>`__

Rfhub2-cli limitation with Docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
While running web server using docker is really easy and advised, running `rfhub2-cli` is cumbersome.
CLI is using internal robotframework tool called `LibDoc`, which requires each library to be installed, in order to create documentation and, later, populating app.
