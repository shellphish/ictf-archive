#!/bin/bash
set -e

# Start PostgreSQL (bookworm ships PostgreSQL 15)
PG_VERSION=$(ls /usr/lib/postgresql/ | head -1)
su - postgres -c "/usr/lib/postgresql/${PG_VERSION}/bin/pg_ctl start \
    -D /var/lib/postgresql/${PG_VERSION}/main \
    -l /var/log/postgresql/startup.log" 2>/dev/null || true

# Wait for PostgreSQL to be ready
for i in $(seq 1 20); do
    su - postgres -c "psql -c 'SELECT 1'" >/dev/null 2>&1 && break
    sleep 1
done

# Create user and database
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='queryuser'\" | grep -q 1" 2>/dev/null || \
    su - postgres -c "psql -c \"CREATE USER queryuser WITH PASSWORD '${DB_PASS_VALUE}' NOCREATEDB NOSUPERUSER\""

su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='querydb'\" | grep -q 1" 2>/dev/null || \
    su - postgres -c "createdb -O queryuser querydb"

# Seed employees table with flag in the Bill Gates row
su - postgres -c "psql -d querydb" <<SQL
DROP TABLE IF EXISTS employees;
CREATE TABLE employees (first text, last text, id text, ext integer);
INSERT INTO employees VALUES ('Bill', 'Gates', '${FLAG_VALUE}', 1001);
INSERT INTO employees VALUES ('Steve', 'Ballmer', '2e28c7a753d21765dbe4c2c4e9ccc7f6', 1002);
INSERT INTO employees VALUES ('John', 'Fink', '106463e472f6cc4e4b5d42aa9f573a51', 1011);
INSERT INTO employees VALUES ('Christopher', 'Schmidt', '78f0e5a0fa4dfd4c3a3f21cb86ae3f1a', 1012);
INSERT INTO employees VALUES ('Brian', 'Black', '649bdf211c086fc5c674fcc77da1c0fb', 1013);
INSERT INTO employees VALUES ('William', 'Blake', '611a440c4517879ff5506f54ba07d4bf', 1014);
GRANT ALL ON employees TO queryuser;
SQL

# Apache CGI scripts use ./templates/header.html relative to the script dir
# ScriptAlias maps /cgi-bin/ to /var/www/cgi-bin/, so CWD is /var/www/cgi-bin/
exec apache2ctl -D FOREGROUND
