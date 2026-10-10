#!/bin/sh
set -e
echo "${FLAG}" > /home/challenge/flag.txt
chmod 444 /home/challenge/flag.txt
exec "$@"
