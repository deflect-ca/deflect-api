#!/bin/sh
echo "Waiting for mysql..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "mysql started"

exec "$@"
