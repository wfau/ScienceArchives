FROM python:3.11

COPY ./src src
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/src"

RUN pip install --upgrade pip

RUN \
    pip install \
        dagster \
        dagster-webserver \
        dagster-postgres \
        dagster-k8s \
        pandas \
        pyspark \
        bs4


WORKDIR /src

# Expose the port that your Dagster instance will run on
EXPOSE 3000

CMD ["dagster", "dev", "-m", "vvx_dagster.definitions", "-h", "0.0.0.0", "-p", "3000"]