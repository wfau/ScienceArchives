# MOONS Django Server

## Docker Compose

Copy the environment template `env-template` to `.env` and update the entries as required.

Generate a secret key with
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Create a files directory `server/files/moons-web` for storing query results.

Build the image:
```
docker compose build
```

Start the containers with django, database, celery worker, celerybeat:
```
docker compose up -d
```

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
