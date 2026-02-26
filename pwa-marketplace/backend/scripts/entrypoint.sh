#!/bin/sh
# Above line:
# For production use: #!/bin/sh
# For debugging (with bashdb): #!/usr/bin/env bash
 
# Entrypoint: Assemble runtime environment and then exec the provided CMD
# Priority:
#  1) If DATABASE_URL is already set, leave it untouched
#  2) Otherwise read DB password from a Docker secret file (preferred) or env var
#     and export DATABASE_URL so the application and CLI tools can consume it
# Notes: This script runs once at container start. It should be idempotent and
# end with `exec "$@"` so the application server (e.g. gunicorn) becomes PID 1
# and receives signals directly
set -e

# Wait for DB to become available using the repository's wait-for-it.sh helper
# if present. This avoids race conditions when the DB container is still
# initializing. Prefer waiting here (entrypoint) rather than in each worker
MYSQL_HOST="${MYSQL_HOST:-db}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
if [ -x "./scripts/wait-for-it.sh" ]; then
  echo "Waiting for DB at ${MYSQL_HOST}:${MYSQL_PORT} using ./scripts/wait-for-it.sh..."
  ./scripts/wait-for-it.sh "$MYSQL_HOST" "$MYSQL_PORT" echo "DB ready"
elif [ -f "./scripts/wait-for-it.sh" ]; then
  echo "Found wait-for-it.sh but it's not executable; running with bash"
  bash ./scripts/wait-for-it.sh "$MYSQL_HOST" "$MYSQL_PORT" echo "DB ready"
fi

# Build DATABASE_URL from secret file or environment if DATABASE_URL not already set
# -z: True if the string is null (an empty string)
# ":-": corresponds to or (:) + default empty string (-)
if [ -z "${DATABASE_URL:-}" ]; then
  PW_FILE="${MYSQL_PASSWORD_FILE:-/run/secrets/mysql_db_user_password}"
  PASSWORD=""
  # -f: True if file exists and is a regular file
  if [ -f "$PW_FILE" ]; then
    # remove potential CR/LF
    PASSWORD=$(tr -d '\r\n' < "$PW_FILE")
  else
    # :- : corresponds to or (:) + default empty string (-)
    PASSWORD="${PW_FILE:-}"
  fi

  MYSQL_USER="${MYSQL_USER:-db_user}"
  MYSQL_DATABASE="${MYSQL_DATABASE:-marketplace_db}"

  # -n: True if the string length is greater than zero
  if [ -n "$PASSWORD" ]; then
    export DATABASE_URL="mysql+pymysql://${MYSQL_USER}:${PASSWORD}@${MYSQL_HOST}:3306/${MYSQL_DATABASE}"
  fi
fi

# Added just for Dev purposes: show DATABASE_URL at log
# echo "DATABASE_URL=$DATABASE_URL" 1>&2

# Exec the passed command (gunicorn or any other)
exec "$@"
