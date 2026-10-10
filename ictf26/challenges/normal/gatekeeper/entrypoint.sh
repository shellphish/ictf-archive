#!/bin/sh
set -e
echo "${FLAG:-ictf{bobby_table_for_LLMs}}" > /flag
chmod 444 /flag
exec "$@"
