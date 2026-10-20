python -m py_compile powerplan.py Board.py
mv powerplan.pyc Board.pyc $DESTDIR/usr/ctf/$SERVICE_USER
install start.sh stop.sh $DESTDIR/usr/ctf/$SERVICE_USER
