cd /usr/ctf/egoats
/sbin/start-stop-daemon -b --start --chdir /usr/ctf/egoats --exec /usr/local/bin/rails s -- > /dev/null
