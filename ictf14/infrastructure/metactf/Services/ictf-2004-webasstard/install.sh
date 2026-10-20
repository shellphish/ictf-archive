gcc -o $DESTDIR/usr/ctf/$SERVICE_USER/$SERVICE_USER $SERVICE_USER.c mydiag.c zocket.c -lssl -lcrypto -m32
install webasstard.pem webasstard.key $DESTDIR/usr/ctf/$SERVICE_USER/
cp -r webdocs/ $DESTDIR/var/ctf/$SERVICE_USER/webdocs
