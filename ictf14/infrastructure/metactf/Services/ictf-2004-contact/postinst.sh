chmod -R 755 /usr/ctf/$SERVICE_USER/
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS corpdb;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE corpdb;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP TABLE IF EXISTS corpdb.employees;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE corpdb.employees(last varchar(200), first varchar(200), extension varchar(200));"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL ON corpdb.* TO 'corpdbuser'@'localhost' IDENTIFIED BY 'basstard';"
a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
