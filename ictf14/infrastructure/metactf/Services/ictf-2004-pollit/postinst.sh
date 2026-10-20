a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
mkdir -p /var/ctf/ictf-2004-pollit/data
ln -s /var/ctf/ictf-2004-pollit/data /usr/ctf/ictf-2004-pollit/html/cgi-bin/polls
chown ictf-2004-pollit:ictf-2004-pollit /var/ctf/ictf-2004-pollit/data
