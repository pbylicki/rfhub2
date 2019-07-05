# rfhub-new

[![Build Status](https://travis-ci.org/pbylicki/rfhub-new.svg?branch=master)](https://travis-ci.org/pbylicki/rfhub-new)
[![codecov](https://codecov.io/gh/pbylicki/rfhub-new/branch/master/graph/badge.svg)](https://codecov.io/gh/pbylicki/rfhub-new)
## Development

#### Install dependencies
```
pip install -r requirements.txt -r requirements-dev.txt
```
To run app with Postgres db install additional dependencies:
```
pip install -r requirements-postgres.txt
```
#### Build docker image
To build image using SQLite DB
```
docker build -f docker/Dockerfile -t rfhub-new .
```
To build image using PostgreSQL DB
```
docker build -f docker/Dockerfile-postgres -t rfhub-new-postgres .
```
#### Run application (web server)
To run with default (SQLite) database
```
python -m rfhub2
```
To run with Postgres database
```
RFHUB_DB_URI=postgresql://postgres:postgres@localhost:5432/postgres python -m rfhub2
```
To run application using docker image with default (SQLite) database
```
docker run -it -p 8000:8000 rfhub-new
```
To run application using docker image with Postgres database
```
docker run -it -p 8000:8000 -e RFHUB_DB_URI="postgresql://postgres:postgres@localhost:5432/postgres" rfhub-new-postgres
```
#### Run unit tests
```
python -m unittest rfhub2.tests
```
