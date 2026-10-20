a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are broken, unload it before we load it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
rm -f $DESTDIR/usr/ctf/$SERVICE_USER/public_html/reports
ln -s $DESTDIR/var/ctf/$SERVICE_USER/reports $DESTDIR/usr/ctf/$SERVICE_USER/public_html/reports
rm -f $DESTDIR/usr/ctf/$SERVICE_USER/public_html/cgi-bin/donations.bin
ln -s $DESTDIR/var/ctf/$SERVICE_USER/donations.bin $DESTDIR/usr/ctf/$SERVICE_USER/public_html/cgi-bin/donations.bin

