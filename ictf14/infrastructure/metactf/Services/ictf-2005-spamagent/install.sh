mkdir -p $DESTDIR/etc/apache2/sites-enabled
install $SERVICE_USER.conf $DESTDIR/etc/apache2/sites-enabled/

mkdir -p $DESTDIR/var/ctf/$SERVICE_USER/

cp -r html/ $DESTDIR/var/ctf/$SERVICE_USER/

mkdir -p $DESTDIR/var/ctf/$SERVICE_USER/html/cgi-bin

gcc -c -DHAVE_STDARG_H=1 -DHAVE_VPRINTF=1 mydiag.c
gcc -c zocket.c
gcc -I/usr/include/libxml2 -o $DESTDIR/var/ctf/$SERVICE_USER/html/cgi-bin/$SERVICE_USER $SERVICE_USER.c -lxml2 -ltcl mydiag.o zocket.o
rm *.o
