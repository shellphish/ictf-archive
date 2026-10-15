#!/bin/bash
# sfind listens on UDP 31337 and double-forks to daemonize.
# We start it then keep the container alive.
cd /var/sfind
su -s /bin/bash sfind -c "/var/sfind/sfind" &
exec sleep infinity
