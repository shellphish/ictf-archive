cp -r html/ $DESTDIR/var/ctf/$SERVICE_USER
mkdir -p $DESTDIR/etc/apache2/sites-enabled
install $SERVICE_USER.conf $DESTDIR/etc/apache2/sites-enabled/
