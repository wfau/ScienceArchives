# set builds as phony so they run, docker is fast if nothing to do
.PHONY: build, build-develop

# loads env settings from .env file
include .env
export

# Runs the prod container at localhost:$(port)
serve: build
	docker run --env-file .env --rm -p $(PUBLISH_PORT):$(PORT) vo-registry

build:
	docker build -t vo-registry --target production .

lint: build-develop
	docker run --rm -v ./:/app vo-registry-dev poetry run black --check ./
	docker run --rm -v ./:/app vo-registry-dev poetry run flake8 ./
	docker run --env-file .env --rm -v ./:/app vo-registry-dev poetry run mypy --disallow-untyped-defs vo_registry

black: build-develop
	docker run --rm -v ./:/app vo-registry-dev poetry run black ./

# Runs unit tests while binding the local directory
test: build-develop
	docker run --env-file .env --rm -v ./:/app vo-registry-dev poetry run pytest tests/unit

# Run E2E tests locally with docker
test-e2e: build
	-docker network create registry-e2e
	-docker run --env-file .env -d -v ./:/app -p $(PORT):$(PORT) --name registry --network registry-e2e vo-registry
	-docker run --env-file .env --rm -v ./:/app --network registry-e2e vo-registry-dev poetry run pytest --runxfail tests/e2e/
	docker container stop registry
	docker container rm registry
	docker network rm registry-e2e

# Run E2E tests against the deployed app
test-deployed:
	-docker run --env-file .env --rm -v ./:/app vo-registry-dev poetry run pytest tests/e2e/ -k 'not landing and not static'

build-develop:
	docker build -t vo-registry-dev --target development .

# Launchs an interactive shell into the dev container
# while binding the local directory
# useful for updating dependencies with poetry
# Using `poetry add`  or `poetry update` from this shell
# will update the lock file in the local directory
develop: build-develop
	docker run -it -v ./:/app vo-registry-dev /bin/bash

# Runs the dev container and binds the local directory
# so it reloads on code changes
serve-develop: build-develop
	docker run --env-file .env  --rm -v ./:/app -p $(PUBLISH_PORT):$(PORT) vo-registry-dev
