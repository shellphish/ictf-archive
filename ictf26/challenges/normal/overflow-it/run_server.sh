#!/usr/bin/env sh
set -eu

cd /app
exec /usr/local/bin/python -u /app/server.py
