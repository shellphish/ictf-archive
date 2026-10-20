gcc -o $DESTDIR/usr/ctf/$SERVICE_USER/discussit discussit.c
cp -r discussit-words/ $DESTDIR/usr/ctf/$SERVICE_USER/
install discussit-chat discussit-main.dict discussit-syn.dict $DESTDIR/usr/ctf/$SERVICE_USER/
cp -r html $DESTDIR/usr/ctf/$SERVICE_USER/html
mkdir -p $DESTDIR/etc/apache2/sites-enabled/
install $SERVICE_USER.conf $DESTDIR/etc/apache2/sites-enabled/

