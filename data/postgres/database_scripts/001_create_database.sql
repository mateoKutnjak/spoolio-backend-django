DO 
$do$ 
BEGIN 
    IF NOT EXISTS (
        SELECT
        FROM pg_catalog.pg_roles -- SELECT list can be empty for this
        WHERE rolname = 'spoolio_web_user'
    ) THEN CREATE ROLE spoolio_web_user LOGIN PASSWORD 'lava-poultice-clatter-zinc';
    END IF;
END 
$do$;

SELECT 'CREATE DATABASE spoolio_web_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spoolio_web_db')\gexec
GRANT ALL PRIVILEGES ON DATABASE spoolio_web_db TO spoolio_web_user;