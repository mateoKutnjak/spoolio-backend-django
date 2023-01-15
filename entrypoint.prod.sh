#!/bin/bash

#Define cleanup procedure
on_shutdown() {
    echo "Shutting down signal"
#    DATABASE_BACKUP=/code/photours/fixtures/on_shutdown_save.json
#    echo "Container stopped, saving database to " $DATABASE_BACKUP
#    python3 /code/photours/manage.py dumpdata photours > $DATABASE_BACKUP
#    # Remove first line of the file
#    tail -n +2 "$DATABASE_BACKUP" > "$DATABASE_BACKUP.tmp" && mv "$DATABASE_BACKUP.tmp" "$DATABASE_BACKUP"
#    return
}

#Trap SIGTERM
trap 'on_shutdown' TERM INT

if [[ "$DATABASE" = "postgres" ]]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

export DJANGO_SETTINGS_MODULE=spoolio_backend.settings

#echo "Flushing database..."
#python3 ${HOME}/app/toqo/manage.py flush --no-input
echo "Migrating database..."
python3 ${HOME}/app/toqo/manage.py migrate
echo "Collect static files..."
python3 ${HOME}/app/toqo/manage.py collectstatic --no-input
# echo "Loading fixtures..."
# python3 ${HOME}/app/toqo/manage.py loaddata ${HOME}/app/toqo/fixtures/backup.json
#echo "Fixtures loaded..."

exec "$@"
