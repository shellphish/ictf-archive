mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS Contributions;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE Contributions;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE Contributions.contributors ( id int(32), name varchar(256), amount int(32), address varchar(256), ccn varchar(32) );"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL PRIVILEGES ON Contributions.* TO 'contribute'@'localhost' identified by 'GoFuckYourself123';"
a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart
