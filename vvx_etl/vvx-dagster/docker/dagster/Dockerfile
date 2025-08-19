FROM python:3.12-slim

# Install system deps
RUN apt-get update && apt-get install -y gcc git build-essential curl

# Install Dagster and tools
RUN pip install dagster dagster-webserver dagster-k8s dagster-postgres

# Copy your code
WORKDIR /app
COPY . /app

# Set entrypoint for Dagster webserver
CMD ["dagster", "webserver", "-h", "0.0.0.0", "-p", "3000"]
