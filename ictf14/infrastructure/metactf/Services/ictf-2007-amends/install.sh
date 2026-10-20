cp -r html/ php-include/ images/ $DESTDIR/usr/ctf/$SERVICE_USER
mkdir -p $DESTDIR/etc/apache2/sites-enabled
install $SERVICE_USER.conf $DESTDIR/etc/apache2/sites-enabled/
cp -r settlement $DESTDIR/var/ctf/$SERVICE_USER
ln -s /var/ctf/$SERVICE_USER/settlement $DESTDIR/usr/ctf/$SERVICE_USER/settlement
# NOTE do something about php.ini here
