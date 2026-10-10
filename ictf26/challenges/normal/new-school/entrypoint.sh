#!/bin/sh
set -e
echo "${FLAG}" > /flag.txt
chmod 444 /flag.txt
exec "$@"
