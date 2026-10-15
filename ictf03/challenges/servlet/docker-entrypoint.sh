#!/bin/bash
set -e

# Start PostgreSQL (bullseye ships PostgreSQL 13)
PG_VERSION=$(ls /usr/lib/postgresql/ | head -1)
su - postgres -c "/usr/lib/postgresql/${PG_VERSION}/bin/pg_ctl start \
    -D /var/lib/postgresql/${PG_VERSION}/main \
    -l /var/log/postgresql/startup.log" 2>/dev/null || true

# Wait for PostgreSQL to be ready
for i in $(seq 1 20); do
    su - postgres -c "psql -c 'SELECT 1'" >/dev/null 2>&1 && break
    sleep 1
done

# Create DB user and database
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='kb'\" | grep -q 1" 2>/dev/null || \
    su - postgres -c "psql -c \"CREATE USER kb WITH PASSWORD '${DBPASSWORD_VALUE}' NOCREATEDB NOSUPERUSER\""

su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='kb'\" | grep -q 1" 2>/dev/null || \
    su - postgres -c "createdb -O kb kb"

# Populate the kb table with the flag
su - postgres -c "psql -d kb" <<SQL
DROP TABLE IF EXISTS kb;
DROP SEQUENCE IF EXISTS kb_id_seq;
CREATE SEQUENCE kb_id_seq;
CREATE TABLE kb(
  id integer PRIMARY KEY DEFAULT nextval('kb_id_seq'),
  title text NOT NULL,
  info text NOT NULL
);
GRANT ALL ON TABLE kb TO kb;
GRANT ALL ON kb_id_seq TO kb;

INSERT INTO kb(title, info) VALUES (
  '"Suspicious" registry key: NSA-${FLAG_VALUE}',
  'The registry key NSA-${FLAG_VALUE} references vital data for the proper functioning of Windows.'
);
INSERT INTO kb(title, info) VALUES (
  'New Linux-based Windows servers too stable',
  'Some users have reported that our new product line which incorporates a Linux-based kernel is too stable.'
);
INSERT INTO kb(title, info) VALUES (
  'Value of MCSE certification negatively impacted',
  'Some MCSE-certified system administrators have complained that their certifications are now worthless.'
);
SQL

# Start Tomcat 9 in foreground
exec /usr/share/tomcat9/bin/catalina.sh run
