python -O -m compileall mulemassageappointment.py
mv mulemassageappointment.pyo $DESTDIR/usr/ctf/$SERVICE_USER
cp *.jpg $DESTDIR/usr/ctf/$SERVICE_USER
install start.sh stop.sh $DESTDIR/usr/ctf/$SERVICE_USER
