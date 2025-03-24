# MOONS Django Server

## Docker Compose

### Set up environment

Copy the environment template `env-template` to `.env` and update the entries as required.

1.  Choose the deployment
    ```
    DEPLOYMENT=local
    ```
    or
    ```
    DEPLOYMENT=production
    ```
    The local deployment will update automatically when changes are made to the source.

1.  Generate a secret key with
    ```
    python -c 'import secrets; chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"; print("".join(secrets.choice(chars) for i in range(50)))'
    ```

    and store it in the variable `SECRET_KEY`.

    (This is how Django creates a secret key)
    ```
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
    ```

1.  Specify the path of the query database and the driver:
    ```
    QUERY_DB_DRIVER=adbc_driver_sqlite.dbapi
    QUERY_DB_CONNECTION=file:///app/resources/mock-gesiDR5.sqlite3
    ```

    ADBC (Arrow Database Connectivity) https://arrow.apache.org/adbc/current/index.html provides drivers for SQLite and Postgres.
    (The file `mock-gesiDR5.sqlite3` is a mock database for testing.)

1.  Choose a superuser for Django. The user will be created on startup but not changed if it exists already.
    ```
    DJANGO_SUPERUSER_USERNAME=moons
    DJANGO_SUPERUSER_PASSWORD=somepass999
    DJANGO_SUPERUSER_EMAIL=someone@example.com
    ````

### Build

Build the image.
```
docker compose build
```
This only needs to be done before the first run, or when there are updates.

### Configure containers

In `docker-compose.yaml` select the ports to expose for the proxy server:
```
services:
  proxy:
    ports:
      - 9000:80
```

For the production deployment this would be
```
services:
  proxy:
    ports:
      - 80:80
      - 443:443
```

Choose the number of replicas for the workers that run SQL queries:
```
  celery_worker:
    deploy:
      mode: replicated
      replicas: 1
```

### Run server

Start docker compose in detached mode, running containers with django, database, celery worker, celerybeat:
```
docker compose up -d
```

### Shut down

Stop containers:
```
docker compose down
```

## Manual Set Up

### Prerequisites

Create a Python environment and install the requirements.

Generate a new secret key:
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
and write the value to `SECRET_KEY` in `moons/settings.py`.

Create an admin user in Django:
```
python manage.py createsuperuser
```

Migrate the databases:
```
python manage.py migrate
```

### Celery

Set up RabbitMQ as a messaging service for background tasks in Celery.

To run Celery as a test server:

```
celery -A moons worker -l INFO
```

### Start server

Start the server (default port is 8000):
```
python manage.py runserver
```

or provide a port
```
python manage.py runserver 5000
```
