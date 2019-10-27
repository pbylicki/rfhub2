# rfhub2

[![Build Status](https://travis-ci.org/pbylicki/rfhub2.svg?branch=master)](https://travis-ci.org/pbylicki/rfhub2)
[![codecov](https://codecov.io/gh/pbylicki/rfhub2/branch/master/graph/badge.svg)](https://codecov.io/gh/pbylicki/rfhub2)
[![image](https://img.shields.io/pypi/v/rfhub2.svg)](https://pypi.org/project/rfhub2/)
[![image](https://img.shields.io/pypi/pyversions/rfhub2.svg)](https://pypi.org/project/rfhub2/)
[![image](https://img.shields.io/pypi/wheel/rfhub2.svg)](https://pypi.org/project/rfhub2/)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/pbylicki/rfhub2.svg)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/pbylicki/rfhub2.svg)

## Introduction
RfHub2 is an opensource project aimed to provide nice and easy way of collecting, browsing and sharing documentation 
of existing keywords written in RobotFramework and python. Built with [Material-UI](https://material-ui.com/) 
and [FastAPI](https://fastapi.tiangolo.com/), served by [Uvicorn](https://www.uvicorn.org/).\
Project is inspired by [robotframework-hub](https://github.com/boakley/robotframework-hub) 
created by Bryan Oakley and can be treated as its spiritual successor.

RfHub2 is hosted on [GitHub](https://github.com/pbylicki/rfhub2), where sourcecode, current issues and additional documentation can be found.

## Installation
#### As python package
latest version can be installed from PyPi:
```
pip install rfhub2
```
or directly from source code:
```
python setup.py install
```
#### With docker
pull docker image with SQLite:
```
docker pull pbylicki/rfhub2
```
or PostgreSQL:
```
docker pull pbylicki/rfhub2:postgres
```
## Starting application
#### Run application (web server)
To run with default (SQLite) database:
```
rfhub2
```
To run with PostgreSQL database:
```
RFHUB_DB_URI=postgresql://postgres:postgres@localhost:5432/postgres rfhub2
```
To run application using docker image with default (SQLite) database:
```
docker run -it -p 8000:8000 rfhub2
```
To run application using docker image with Postgres database:
```
docker run -it -p 8000:8000 --network=host -e RFHUB_DB_URI="postgresql://postgres:postgres@localhost:5432/postgres" rfhub2:postgres
```
#### Populate application with data
To populate application running on localhost:
```
rfhub2-cli ../your_repo ../your_other_repo
```
To populate app running on another host, with non-default credentials:
```
rfhub2-cli -a http://your_host:8000 -u user -p password ../your_repo ../your_other_repo
```
To populate app but to skip loading RFWK installed libraries:
```
rfhub2-cli --no-installed-keywords ../your_repo ../your_other_repo
```
#### Rfhub2-cli can be run in three modes:

- `insert`, default mode, that will clean up existing collections app and load all collections found in provided paths  
``` rfhub2-cli mode=insert ../your_repo ../your_other_repo```
- `append`, which will only add collections form provided paths  
``` rfhub2-cli mode=append ../your_repo ../your_other_repo```
- `update`, which will compare existing collections with newly found ones, and update existing, remove obsolete and add new ones  
``` rfhub2-cli mode=update ../your_repo ../your_other_repo```

## License
RfHub2 is an open source software provided under the [Apache License 2.0](http://apache.org/licenses/LICENSE-2.0)
