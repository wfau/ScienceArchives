# Based on https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service
# and https://github.com/orgs/python-poetry/discussions/1879#discussioncomment-216865

FROM python:3.12-slim AS base

LABEL org.opencontainers.image.source=https://github.com/wfau/ScienceArchives


# python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1


RUN pip install pipx
RUN pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# copy project requirement files here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./

# Needs a few things to install the current package
RUN mkdir vo_registry; touch vo_registry/__init__.py; touch README.md
RUN poetry install --without dev

ENV PORT=8080
EXPOSE 8080


## DEV BUILD

# `development` image is used during development / testing
FROM base AS development

RUN poetry install

COPY ./ ./

# https://cloud.google.com/run/docs/issues#home
CMD HOME=/root exec poetry run uvicorn --reload --host 0.0.0.0 --port $PORT vo_registry.main:app


## PROD BUILD

FROM base AS production

COPY ./vo_registry ./vo_registry

# https://cloud.google.com/run/docs/issues#home
CMD HOME=/root exec poetry run uvicorn --port $PORT --host 0.0.0.0 vo_registry.main:app