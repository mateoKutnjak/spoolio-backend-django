#!/bin/bash

if [[ "$DATABASE" = "postgres" ]]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

export DJANGO_SETTINGS_MODULE=spoolio_backend.settings

echo "Migrating database..."
python3 ${HOME}/app/manage.py migrate
echo "DONE"

exec "$@"