# VO Registry

The VO Registry is a FastAPI Python service that provides the necessary features
to run a publishing registry that implements the OAI-PMH protocol. For more information
about VO publishing registries see the [main README file](../README.md) and the
[IVOA Resource Registry Documentation](https://wiki.ivoa.net/twiki/bin/view/IVOA/IvoaResReg).

## System Requirements

| Name          | Required Version | Details                                       |
|---------------|------------------|-----------------------------------------------|
| Docker Engine | `27+`            | Required for all environments                 |
| Make          | `4.3+`           | **Note:** only required for local development |

## Environment Variables

| Environment | Variable                   | Description                                                      | Example                  |
|-------------|----------------------------|------------------------------------------------------------------|--------------------------|
| `.env`      | `BASE_URL`                 | The external url of the service.                                 | `https://vo.noirlab.edu` |
|             | `PORT`                     | The port of the API service                                      | `8080`                   |
|             | `PUBLISH_PORT`             | Port to publish the container. Used in development scripts only. | `8080`                   |
| `Gitlab CI` | `SERVICE_ACCOUNT_EMAIL`    | a terraform output                                               | ``                       |
|             | `WI_POOL_PROVIDER`         | a terraform output                                               | ``                       |
|             | `TF_VAR_gitlab_project_id` | the gitlab project id (integer)                                  | ``                       |
|             | `TF_VAR_google_project_id` | the google project id                                            | ``                       |

## Configuration

After forking the repository.

- Update `config.py` with your name and email
- Update static Resource files: `authority.xml` and `registry.xml`

## Steps to Run

You can run the application in your local Docker environment. For convenience, various
commands are defined in the Makefile. After starting the application it will be accessible
at `http://localhost:8080/registry` (or the port you defined in the `PORT` setting)

### Make

This will run a series of commands to build and start the application

```sh
make
```

### Docker

You can also build and run the registry using the Docker API directly

Build the image:  

```sh
docker build -t vo-registry-dev --target development .
```

Run a container:

```sh
docker run --env-file .env --rm -p 8080:8000 vo-registry
```

## Testing

Various test suites are provided and include unit tests and end-to-end tests.

To run the unit tests:

```sh
make test
```

To run the end-to-end tests:

```sh
make test-e2e
```

You can also run the end-to-end tests on a remote registry by setting the `BASE_URL`:

```sh
make BASE_URL=https://template.vo.noirlab.edu test-deployed
```

## Development

A [Makefile](Makefile) is provided that contains various commands useful for
development. See the comments in the Makefile for usage.

### Commit Hooks

[Pre-commit](https://pre-commit.com/) can be installed to automate the code
quality and formatting adjustments and the `.pre-commit-config.yaml` file defines
the hooks. It is recommended to activate these during the development setup step to
avoid manual checks and extra commits for formatting. These checks also happen
in the Gitlab CI for those that like to run them manually.

To setup the git hooks, after installing the dev dependencies run:

```sh
pre-commit install
```

## System Design

This application is a python
[FastAPI](https://fastapi.tiangolo.com/) app that implements
the required components of the
[OAI-PMH specification](http://www.openarchives.org/OAI/openarchivesprotocol.html) to be a valid
[VO Registry](https://ivoa.net/documents/RegistryInterface/20180723/REC-RegistryInterface-1.1.html).

[VOResources](https://www.ivoa.net/documents/latest/VOResource.html)
are defined as static files in the `vo_registry/static/resources/`
directory. The two required VOResources are included (Registry and Authority).
Additional resources specific to your services can be added to the static directory
as YAML, JSON or XML.

**Note** The resource files must be in the root static directory, nested directories
are not supported.

**Note:** This registry does not implement Sets or Metadata Formats besides the required
"ivo_managed" set and "ivo_vor/oai_dc" metadata formats.

**Note:** This registry does not implement pagination and resumption tokens will
produce an error.
