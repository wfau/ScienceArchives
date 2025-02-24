# MOONS Django Server

## Set up

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

## Celery

Set up RabbitMQ as a messaging service for background tasks in Celery.

To run Celery as a test server:

```
celery -A moons worker -l INFO
```

## Start server

Start the server (default port is 8000):
```
python manage.py runserver
```

or provide a port
```
python manage.py runserver 5000
```
