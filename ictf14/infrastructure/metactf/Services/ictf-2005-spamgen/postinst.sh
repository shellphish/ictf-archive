mv /usr/ctf/$SERVICE_USER/apache2.conf /etc/apache2/
mv /usr/ctf/$SERVICE_USER/$SERVICE_USER.conf /etc/apache2/sites-enabled/
chmod -R 755 /usr/ctf/$SERVICE_USER
a2dismod deflate
a2enmod cgi
service apache2 restart
chown www-data /usr/ctf/$SERVICE_USER/html/cgi-bin/user_db
chown www-data /usr/ctf/$SERVICE_USER/html/cgi-bin/spamgen.py
