#!/bin/sh
/sbin/start-stop-daemon \
    --stop \
    --pidfile /var/ctf/curiosityblogging//running.pid
killall nodejs
