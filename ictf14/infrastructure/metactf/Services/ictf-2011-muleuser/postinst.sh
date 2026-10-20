a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi

service apache2 restart
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS mulemanager;"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE mulemanager;"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP TABLE IF EXISTS mulemanager.users;"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE mulemanager.users (username VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY,password VARCHAR(128) NOT NULL,email VARCHAR(128),first_name VARCHAR(128),last_name VARCHAR(128),phone VARCHAR(128),affiliation VARCHAR(128),address VARCHAR(128),city VARCHAR(128),state VARCHAR(128),zipcode VARCHAR(128),country VARCHAR(128),cookie VARCHAR(128) DEFAULT NULL);"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP TABLE IF EXISTS mulemanager.groups;"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE mulemanager.groups (groupname VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY);"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL PRIVILEGES ON mulemanager.* TO 'mulemanager'@'localhost' identified by 'grabthiswhileyoucan';"
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e  "INSERT INTO groups (groupname) VALUES (\"good mules\");" mulemanager
mysql  --defaults-extra-file=/etc/mysql/debian.cnf -e  "INSERT INTO groups (groupname) VALUES (\"bad mules\");" mulemanager
#chown www-data /usr/ctf/$SERVICE_USER/html/cgi-bin/messages
