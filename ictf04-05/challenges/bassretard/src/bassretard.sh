#!/bin/sh
# This starts and stops bassretard.
# description: bassretard is a powerful system administartion tool \
#              bassretard is specifically designed to be unbreakable and \
#              has access control mechanisms, and extensive \
#              logging capabilities among other things.


test -f /usr/local/bin/bassretard || exit 0
test -f /usr/local/share/bassretard/basstard.css || exit 0

PATH=/sbin:/bin:/usr/bin:/usr/sbin:/usr/local/bin
BASSUSER=bassretard

case "$1" in
start)  echo -n "Starting bassretard daemon: "
        start-stop-daemon --start --quiet --user ${BASSUSER} --chuid ${BASSUSER} --exec /usr/local/bin/bassretard -- --daemon
        echo "."
        ;;
stop)   echo -n "Stopping bassretard daemon: "
        start-stop-daemon --stop --quiet --user ${BASSUSER} --exec /usr/local/bin/bassretard
        echo "."
        ;;
restart|reload|force-reload) echo -n "Restarting bassretard daemon: "
        start-stop-daemon --stop --retry 5 --quiet --user ${BASSUSER} --exec /usr/local/bin/bassretard
        start-stop-daemon --start --quiet --user ${BASSUSER} --chuid ${BASSUSER} --exec /usr/local/bin/bassretard -- --daemon
        echo "."
        ;;
*)      echo "Usage: /etc/init.d/cron start|stop|restart|reload|force-reload"
        exit 1
        ;;
esac
exit 0
