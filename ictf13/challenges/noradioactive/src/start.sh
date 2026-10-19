echo "start start"

cd /usr/ctf/noradioactive

echo "post cd"

/sbin/start-stop-daemon -b --name=cassandra --start --chdir /var/ctf/noradioactive --exec /usr/ctf/noradioactive/cassandra/bin/cassandra -- > /dev/null

echo "pre waiter"

./wait_cassandra.py

echo "post waiter"


/sbin/start-stop-daemon -b --name=noradioactive --start --chdir /var/ctf/noradioactive --exec /usr/bin/python /usr/ctf/noradioactive/noradioactive.pyo --

echo "start done"

