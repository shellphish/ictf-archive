python -m py_compile traintrain.py generate_assignment.py
mv traintrain.pyc $DESTDIR/usr/ctf/$SERVICE_USER/traintrain
mv generate_assignment.pyc $DESTDIR/usr/ctf/$SERVICE_USER/generate_assignment
cp traintrain.db $DESTDIR/var/ctf/$SERVICE_USER/.
install start.sh stop.sh $DESTDIR/usr/ctf/$SERVICE_USER

