python -O -t -t -m compileall $SERVICE_USER.py
mv $SERVICE_USER.pyo $DESTDIR/usr/ctf/$SERVICE_USER
cp -f wait_cassandra.py $DESTDIR/usr/ctf/$SERVICE_USER
cp -r apache-cassandra-2.0.8 $DESTDIR/usr/ctf/$SERVICE_USER/cassandra/
mkdir -p $DESTDIR/var/ctf/$SERVICE_USER/cassandra
