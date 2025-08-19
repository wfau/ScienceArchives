FROM apache/spark:3.5.5

# Install PostgreSQL JDBC driver
RUN curl -L -o /opt/spark/jars/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.6.0.jar

WORKDIR /app
COPY . /app