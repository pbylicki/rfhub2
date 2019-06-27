# rfhub-new

## Development

#### Install dependencies
```
pip install -r requirements.txt -r requirements-dev.txt
```

To run app with Postgres db install additional dependencies:
```
pip install -r requirements-postgres.txt
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

#### Run unit tests
```
python -m unittest rfhub2.tests
```
