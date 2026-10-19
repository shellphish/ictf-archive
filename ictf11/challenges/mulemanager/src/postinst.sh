# Apache site
service apache2 restart

# MySQL database
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS mulemanager;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE mulemanager;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL PRIVILEGES ON mulemanager.* TO 'mulemanager'@'localhost' identified by 'grabthiswhileyoucan'"

# users
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "DROP TABLE IF EXISTS mulemanager.users;"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "CREATE TABLE mulemanager.users (username VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY,password VARCHAR(128) NOT NULL,email VARCHAR(128),first_name VARCHAR(128),last_name VARCHAR(128),phone VARCHAR(128),affiliation VARCHAR(128),address VARCHAR(128),city VARCHAR(128),state VARCHAR(128),zipcode VARCHAR(128),country VARCHAR(128),cookie VARCHAR(128) DEFAULT NULL);"
# endpoints
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "DROP TABLE IF EXISTS mulemanager.endpoints;"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "CREATE TABLE mulemanager.endpoints (id INT UNSIGNED AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,username VARCHAR(128) NOT NULL,type VARCHAR(128) NOT NULL,address VARCHAR(128) NOT NULL,carrier VARCHAR(128),data VARCHAR(256));"
# groups
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "DROP TABLE IF EXISTS mulemanager.groups;"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "CREATE TABLE mulemanager.groups (groupname VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY);"
# group_users
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "DROP TABLE IF EXISTS mulemanager.groups_users;"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "CREATE TABLE mulemanager.groups_users (groupname VARCHAR(128) NOT NULL,username VARCHAR(128) NOT NULL);"

mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"admin\", \"admin\", \"Leet\", \"Admin\", \"admin@muleserver\", \"+1 (666) 666-6666\", \"Muleserver, Inc.\", \"Mule Road\", \"Mule City\", \"CA\", \"93891\", \"USA\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"jdoe\", \"doedoe\", \"John\", \"Doe\", \"jdoe@foo.com\", \"+1 (805) 893-6151\", \"The Unknown, Inc.\", \"1288 Overlook Ln\", \"Santa Barbara\", \"CA\", \"93111\", \"USA\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"jdee\", \"updog\", \"Jane\", \"Dee\", \"jdee@bar.com\", \"+1 (650) 112-1337\", \"The Missing L, Inc.\", \"Laguna Blanca Pl\", \"San Jose\", \"CA\", \"95014\", \"USA\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"mark\", \"barfoo\", \"Mark\", \"Maglietta\", \"mark@barfoo.com\", \"+1 (811) 455-7232\", \"Mule Paradise\", \"Hacker Lane\", \"Goleta\", \"CA\", \"93117\", \"USA\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) VALUES (\"bark\", \"bluetree\", \"Brian\", \"Ark\", \"bark@bark.com\", \"+1 (478) 911-6091\", \"Redneck Mules\", \"Banjo Street\", \"East Dublin\", \"GA\", \"31027\", \"USA\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO groups (groupname) VALUES (\"good mules\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO groups (groupname) VALUES (\"bad mules\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO groups_users (groupname, username) VALUES (\"good mules\", \"jdoe\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO groups_users (groupname, username) VALUES (\"good mules\", \"jdee\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO groups_users (groupname, username) VALUES (\"bad mules\", \"mark\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO groups_users (groupname, username) VALUES (\"bad mules\", \"bark\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"jdoe\", \"sms\", \"+1 (805) 876-1172\", \"Verizon\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"jdoe\", \"sms\", \"+1 (231) 981-3256\", \"Sprint\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"jdoe\", \"email\", \"jdoe@foo.com\", NULL);"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"jdee\", \"sms\", \"+1 (123) 432-7761\", \"Sprint\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"jdee\", \"email\", \"jdee@gmail.com\", NULL);"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"jdee\", \"email\", \"jane.dee@hotmail.com\", NULL);"	
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"mark\", \"sms\", \"+1 (805) 782-2522\", \"Verizon\");"
mysql mulemanager -u mulemanager --password='grabthiswhileyoucan' -e "INSERT INTO endpoints (username, type, address, carrier) VALUES (\"bark\", \"sms\", \"+1 (805) 771-1128\", \"Verizon\");"
service mysql restart
