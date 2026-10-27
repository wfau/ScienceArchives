FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# mssql-python bundles its own ODBC driver but requires libltdl7 at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends libltdl7 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /bench
COPY *.py /bench/

ENTRYPOINT ["python", "/bench/benchmark.py"]