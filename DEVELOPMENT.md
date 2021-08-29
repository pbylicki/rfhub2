## Install dependencies
#### Python
```
pip install -r requirements.txt -r requirements-dev.txt
```
To run app with Postgres db install additional dependencies:
```
pip install -r requirements-postgres.txt
```

#### Frontend

Requirements:
- Node.js
- Yarn

```
cd frontend && yarn install
```

### Build docker image
To build image using SQLite DB:
```
docker build -f docker/Dockerfile -t rfhub2 .
```
To build image using PostgreSQL DB:
```
docker build -f docker/Dockerfile-postgres -t rfhub2:postgres .
```
## Run application (web server)
To run with default (SQLite) database:
```
rfhub2
```
To run with Postgres database:
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

## Frontend
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

### Populate application with data
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
To flush the database and to populate app with collections from provided paths:
```
rfhub2-cli --load-mode=insert ../your_repo ../your_other_repo
```

### Run unit tests
```
python -m unittest tests
```

### Formatting
Black is used for code formatting. It is included in CI pipeline.
To reformat code after edit, execute:
```
black -t py36 rfhub2 tests
```

You can consider adding a git hook or integrating it with your IDE for automated execution.

### Database migrations
When you introduce any changes to database schema, you should prepare Alembic revision reflecting these changes.

To autogenerate revision file, make sure that SQLALCHEMY_DB_URI variable in config points to existing database instance
containing database state from previous revision and execute

```
PYTHONPATH=. alembic -c rfhub2/alembic.ini revision --autogenerate -m "Your revision name"
```
Before commit, inspect generated file to make sure that revision contains only relevant changes to the schema.
