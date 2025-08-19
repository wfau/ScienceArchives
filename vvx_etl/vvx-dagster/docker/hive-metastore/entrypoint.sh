#!/bin/bash

HIVE_DB_USER=$(cat /run/secrets/postgres_user)
HIVE_DB_PASS=$(cat /run/secrets/postgres_password)
HIVE_DB_NAME=$(cat /run/secrets/postgres_db)

export SERVICE_OPTS="
  -Djavax.jdo.option.ConnectionDriverName=org.postgresql.Driver \
  -Djavax.jdo.option.ConnectionURL=jdbc:postgresql://postgres:5432/${HIVE_DB_NAME} \
  -Djavax.jdo.option.ConnectionUserName=${HIVE_DB_USER} \
  -Djavax.jdo.option.ConnectionPassword=${HIVE_DB_PASS}
"

exec /opt/hive/bin/hive --service metastore
