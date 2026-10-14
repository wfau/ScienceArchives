FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# libltdl7 is required by mssql-python's bundled ODBC driver.
# libkrb5-3 / libgssapi-krb5-2 are already present in the slim-bullseye base.
RUN apt-get update && apt-get install -y --no-install-recommends libltdl7 \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install "psycopg[binary]"
RUN pip install mozilla-django-oidc

# Database tooling (postgres_to_mssql.py; deps already in requirements.txt)
COPY ./database/postgres_to_mssql.py /database/postgres_to_mssql.py

# development only
RUN pip install django-cors-headers

COPY ./docker/local/django/start /start
RUN chmod +x /start

COPY ./docker/local/django/celery/worker/start /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/local/django/celery/beat/start /start-celerybeat
RUN chmod +x /start-celerybeat

# COPY ./docker/local/django/celery/flower/start /start-flower
# RUN chmod +x /start-flower

WORKDIR /app

CMD ["/bin/bash"]