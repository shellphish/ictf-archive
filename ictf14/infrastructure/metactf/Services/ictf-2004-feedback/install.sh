cp -r html/ $DESTDIR/usr/ctf/$SERVICE_USER
cp -r var/* $DESTDIR/var/ctf/$SERVICE_USER
mkdir -p $DESTDIR/etc/apache2/sites-enabled
install $SERVICE_USER.conf $DESTDIR/etc/apache2/sites-enabled/
