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

##### Frontend

Requirements:
- Node.js
- Yarn

```
cd frontend && yarn install
```

#### Build docker image
To build image using SQLite DB:
```
docker build -f docker/Dockerfile -t rfhub-new .
```
To build image using PostgreSQL DB:
```
docker build -f docker/Dockerfile-postgres -t rfhub-new-postgres .
```
#### Run application (web server)
To run with default (SQLite) database:
```
python -m rfhub2
```
To run with Postgres database:
```
RFHUB_DB_URI=postgresql://postgres:postgres@localhost:5432/postgres python -m rfhub2
```
To run application using docker image with default (SQLite) database:
```
docker run -it -p 8000:8000 rfhub-new
```
To run application using docker image with Postgres database:
```
docker run -it -p 8000:8000 --network=host -e RFHUB_DB_URI="postgresql://postgres:postgres@localhost:5432/postgres" rfhub-new-postgres
```

##### Frontend
To run frontend development server
```
cd frontend && yarn start
```

To create frontend build
```
yarn build
```
To create frontend build and add its files to rfhub2 package static files directory
```
./build_ui.sh
```

#### Populate application with data
To populate application running on localhost:
```
python -m rfhub2.cli ../your_repo ../your_other_repo
```
To populate app running on another host, with non-default credentials:
```
python -m rfhub2.cli -a http://your_host:8000 -u user -p password ../your_repo ../your_other_repo
```
To populate app but to skip loading RFWK installed libraries:
```
python -m rfhub2.cli --no-installed-keywords ../your_repo ../your_other_repo
```
To preserve previously loaded collections and add new ones:
```
python -m rfhub2.cli --no-db-flush ../your_repo ../your_other_repo
```

#### Run unit tests
```
python -m unittest tests
```

#### Formatting
Black is used for code formatting. It is included in CI pipeline.
To reformat code after edit, execute:
```
black -t py36 rfhub2 tests
```

You can consider adding a git hook or integrating it with your IDE for automated execution.

