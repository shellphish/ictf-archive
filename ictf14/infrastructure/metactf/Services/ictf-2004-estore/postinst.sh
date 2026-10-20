mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS estore;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE estore;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE estore.users(username varchar(200), password varchar(200), firstname varchar(200), lastname varchar(200), email varchar(200), cookie varchar(200));"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL ON estore.* TO 'estoreuser'@'localhost' IDENTIFIED BY 'retard';"
a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
