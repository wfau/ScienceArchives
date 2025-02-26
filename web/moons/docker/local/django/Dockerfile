FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install "psycopg[binary]"

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