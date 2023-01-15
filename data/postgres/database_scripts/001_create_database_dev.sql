DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles  -- SELECT list can be empty for this
      WHERE  rolname = 'spoolio_backend') THEN

      CREATE ROLE spoolio_backend LOGIN PASSWORD 'spoolio_backend';
   END IF;
END
$do$;

SELECT 'CREATE DATABASE spoolio_backend_db_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spoolio_backend_db_dev')\gexec
GRANT ALL PRIVILEGES ON DATABASE spoolio_backend_db_dev TO spoolio_backend;

-- SELECT 'CREATE DATABASE spoolio_backend_prod'
-- WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spoolio_backend_db_prod')\gexec
-- GRANT ALL PRIVILEGES ON DATABASE spoolio_backend_db_prod TO spoolio_backend;