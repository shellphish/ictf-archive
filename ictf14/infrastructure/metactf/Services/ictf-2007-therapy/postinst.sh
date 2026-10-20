rm -rf /var/lib/tomcat6/webapps/Therapy_files /var/lib/tomcat6/webapps/Therapy.war
mv /usr/ctf/$SERVICE_USER/Therapy_files /var/lib/tomcat6/webapps/
mv /usr/ctf/$SERVICE_USER/Therapy.war /var/lib/tomcat6/webapps/
chmod +r /var/lib/tomcat6/webapps/Therapy.war
chmod 755 /var/lib/tomcat6/webapps/Therapy_files/
chmod +r /var/lib/tomcat6/webapps/Therapy_files/*
cp /usr/share/java/mysql.jar /usr/share/tomcat6/lib/
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS psycho;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE psycho;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE psycho.users (id MEDIUMINT NOT NULL AUTO_INCREMENT,username varchar(32),password varchar(32),role ENUM('client', 'counselor'),firstname varchar(32),lastname varchar(32),email varchar(128),counselor varchar(32),private_info varchar(128),description TEXT,PRIMARY KEY (id));"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL PRIVILEGES ON psycho.* TO 'psycho'@'localhost' identified by 'psycho';"
service tomcat6 restart
