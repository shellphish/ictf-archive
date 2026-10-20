a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
rm -f /usr/ctf/museum/html/cgi-bin/museum_ideas
rm -f /usr/ctf/museum/html/cgi-bin/museum_spam
ln -s /var/ctf/museum/museum_ideas /usr/ctf/museum/html/cgi-bin/museum_ideas
ln -s /var/ctf/museum/museum_spam /usr/ctf/museum/html/cgi-bin/museum_spam

