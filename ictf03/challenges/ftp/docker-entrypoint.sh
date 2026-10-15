#!/bin/bash
# ftpd double-forks to daemonize; we start it then keep the container alive.
cd /var/ftp
/usr/local/sbin/ftpd &
exec sleep infinity
