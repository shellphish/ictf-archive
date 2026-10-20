chmod -R 755 /usr/ctf/$SERVICE_USER
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS amends;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE amends;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE amends.pirates(id INT UNSIGNED NOT NULL AUTO_INCREMENT,fname VARCHAR(50) NOT NULL,lname VARCHAR(50) NOT NULL,eaddr VARCHAR(50) NOT NULL,iaddr VARCHAR(20) NOT NULL,price FLOAT(10,2) UNSIGNED NOT NULL,caseid VARCHAR(20) NOT NULL,ccnum  VARCHAR(64) DEFAULT 'N/A',PRIMARY KEY (id),UNIQUE (eaddr),UNIQUE (caseid));"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL PRIVILEGES ON amends.* TO 'amends'@'localhost' IDENTIFIED BY 'YarrImaPirate123';"
a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
