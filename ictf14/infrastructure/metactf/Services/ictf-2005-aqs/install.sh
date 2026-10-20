cp -r html/ $DESTDIR/usr/ctf/$SERVICE_USER/
cp  httpserver.py $DESTDIR/usr/ctf/$SERVICE_USER/
python -m py_compile "library.py"
gcc cprog.c -o cprog -m32
mv library.pyc cprog $DESTDIR/usr/ctf/$SERVICE_USER/html/cgi-bin/
touch $DESTDIR/var/ctf/$SERVICE_USER/guestbook

