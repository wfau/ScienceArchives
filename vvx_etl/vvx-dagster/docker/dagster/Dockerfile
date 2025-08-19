FROM python:3.11

COPY . /
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN \
    pip install \
        dagster \
        dagster-postgres \
        dagster-k8s \
        pandas \
        pyspark


WORKDIR /vvx_pipeline

# Expose the port that your Dagster instance will run on
EXPOSE 3000