DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles  -- SELECT list can be empty for this
      WHERE  rolname = 'toqo') THEN

      CREATE ROLE toqo LOGIN PASSWORD 'toqo';
   END IF;
END
$do$;

SELECT 'CREATE DATABASE toqo_db_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'toqo_db_dev')\gexec
GRANT ALL PRIVILEGES ON DATABASE toqo_db_dev TO toqo;

SELECT 'CREATE DATABASE toqo_db_prod'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'toqo_db_prod')\gexec
GRANT ALL PRIVILEGES ON DATABASE toqo_db_prod TO toqo;