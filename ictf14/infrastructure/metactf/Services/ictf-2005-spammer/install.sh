cp -r html/ $DESTDIR/usr/ctf/$SERVICE_USER
install spammerd.py start.sh stop.sh $DESTDIR/usr/ctf/$SERVICE_USER
mkdir -p $DESTDIR/etc/apache2/sites-enabled
install $SERVICE_USER.conf $DESTDIR/etc/apache2/sites-enabled/
