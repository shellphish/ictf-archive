#!/bin/sh
/sbin/start-stop-daemon \
    --background \
    --start \
    --chuid curiosityblogging \
    --chdir /var/ctf/curiosityblogging/ \
    --make-pidfile \
    --pidfile /var/ctf/curiosityblogging//running.pid \
    --exec /usr/ctf/curiosityblogging//run.sh
