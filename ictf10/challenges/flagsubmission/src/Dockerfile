FROM python:2.7-slim

WORKDIR /app

# Install GPG for flag verification
RUN apt-get update && apt-get install -y --no-install-recommends gnupg && rm -rf /var/lib/apt/lists/*

COPY submission.py /app/submission.py
COPY webserver.ico /app/webserver.ico

# Create an empty SQLite database on first run
# The -i flag initializes the DB schema
# Runtime config files (teams.ini, services.ini) must be mounted or provided

EXPOSE 8080

# Initialize DB and start server.
# teams.ini and services.ini are expected two directories up (../../teams.ini, ../../services.ini)
# in the original deployment; mount them at /config for containerized use.
CMD ["python", "submission.py", "-i", "-p", "8080"]
