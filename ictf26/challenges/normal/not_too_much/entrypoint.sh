#!/bin/sh
set -e
echo "${FLAG}" > /challenge/flag.txt
chmod 444 /challenge/flag.txt
exec "$@"
