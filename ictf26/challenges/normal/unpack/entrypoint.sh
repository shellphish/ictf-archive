#!/bin/sh
set -e
echo "${FLAG}" > /etc/flag.txt
chmod 644 /etc/flag.txt
exec "$@"
