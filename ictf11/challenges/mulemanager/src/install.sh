cp -r html/ $DESTDIR/usr/ctf/$SERVICE_USER
mkdir -p $DESTDIR/etc/apache2/sites-enabled/
install mulemanager.conf  $DESTDIR/etc/apache2/sites-enabled/$SERVICE_USER.conf
