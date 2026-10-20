mv /usr/ctf/$SERVICE_USER/apache2.conf /etc/apache2/
mv /usr/ctf/$SERVICE_USER/$SERVICE_USER.conf /etc/apache2/sites-enabled/
mv /usr/ctf/$SERVICE_USER/my.cnf /etc/mysql/
chmod -R 755 /usr/ctf/$SERVICE_USER
a2dismod deflate
a2enmod cgi
service apache2 restart
mysql -u root -e "DROP DATABASE IF EXISTS mulemanager;"
mysql -u root -e "CREATE DATABASE mulemanager;"
mysql -u root -e "DROP TABLE IF EXISTS mulemanager.users;"
mysql -u root -e "CREATE TABLE mulemanager.users (username VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY,password VARCHAR(128) NOT NULL,email VARCHAR(128),first_name VARCHAR(128),last_name VARCHAR(128),phone VARCHAR(128),affiliation VARCHAR(128),address VARCHAR(128),city VARCHAR(128),state VARCHAR(128),zipcode VARCHAR(128),country VARCHAR(128),cookie VARCHAR(128) DEFAULT NULL);"
mysql -u root -e "DROP TABLE IF EXISTS mulemanager.endpoints;"
mysql -u root -e "CREATE TABLE mulemanager.endpoints (id INT UNSIGNED AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,username VARCHAR(128) NOT NULL,type VARCHAR(128) NOT NULL,address VARCHAR(128) NOT NULL,carrier VARCHAR(128),data VARCHAR(256));"
mysql -u root -e "DROP TABLE IF EXISTS mulemanager.groups;"
mysql -u root -e "CREATE TABLE mulemanager.groups (groupname VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY);"
mysql -u root -e "GRANT ALL PRIVILEGES ON mulemanager.* TO 'mulemanager'@'%' identified by 'grabthiswhileyoucan';"
mysql mulemanager -u root -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"admin\", \"admin\", \"Leet\", \"Admin\", \"admin@muleserver\", \"+1 (666) 666-6666\", \"Muleserver, Inc.\", \"Mule Road\", \"Mule City\", \"CA\", \"93891\", \"USA\");"
mysql mulemanager -u root -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"jdoe\", \"doedoe\", \"John\", \"Doe\", \"jdoe@foo.com\", \"+1 (805) 893-6151\", \"The Unknown, Inc.\", \"1288 Overlook Ln\", \"Santa Barbara\", \"CA\", \"93111\", \"USA\");"
mysql mulemanager -u root -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"jdee\", \"updog\", \"Jane\", \"Dee\", \"jdee@bar.com\", \"+1 (650) 112-1337\", \"The Missing L, Inc.\", \"Laguna Blanca Pl\", \"San Jose\", \"CA\", \"95014\", \"USA\");"
mysql mulemanager -u root -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"mark\", \"barfoo\", \"Mark\", \"Maglietta\", \"mark@barfoo.com\", \"+1 (811) 455-7232\", \"Mule Paradise\", \"Hacker Lane\", \"Goleta\", \"CA\", \"93117\", \"USA\");"
mysql mulemanager -u root -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"bark\", \"bluetree\", \"Brian\", \"Ark\", \"bark@bark.com\", \"+1 (478) 911-6091\", \"Redneck Mules\", \"Banjo Street\", \"East Dublin\", \"GA\", \"31027\", \"USA\");"
mysql mulemanager -u root -e "INSERT INTO groups (groupname) VALUES (\"good mules\");"
mysql mulemanager -u root -e "INSERT INTO groups (groupname) VALUES (\"bad mules\");"
service mysql restart
chown www-data /usr/ctf/ictf-2011-muleadmin/tickets
