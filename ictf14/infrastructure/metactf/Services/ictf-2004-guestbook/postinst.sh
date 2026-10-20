a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart

cd /usr/ctf/$SERVICE_USER/html/cgi-bin
rm -rf data
ln -sf ../../../../../var/ctf/$SERVICE_USER/data .
