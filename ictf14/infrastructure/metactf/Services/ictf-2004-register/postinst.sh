a2dismod deflate
a2dismod mpm_event
a2dismod mpm_worker
# BUG: mpm_itk's unload and load handlers are borken, unload it before we load
# it.  Long story...
a2dismod mpm_itk
a2enmod mpm_itk
a2enmod cgi
service apache2 restart

chmod -R 755 /usr/ctf/$SERVICE_USER

mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS registration;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE registration;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP TABLE IF EXISTS registration.voters;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE TABLE registration.voters (id MEDIUMINT NOT NULL AUTO_INCREMENT KEY,last VARCHAR(200) NOT NULL,first VARCHAR(200) NOT NULL,dob VARCHAR(200) NOT NULL,email VARCHAR(200) NOT NULL,password VARCHAR(200) NOT NULL,wwid VARCHAR(200) NOT NULL UNIQUE);"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT SELECT, INSERT, UPDATE ON registration.voters TO clerk@localhost IDENTIFIED BY 'elections';"
mysql registration -u clerk --password='elections' -e "INSERT INTO registration.voters VALUES(NULL,'Fellini','Federico','Jan 20, 1920','fellini@amarcord.it','volpina','73bb828929783a987d287e4c8==');"
mysql registration -u clerk --password='elections' -e "INSERT INTO registration.voters VALUES(NULL,'Fassbinder','Rainer Werner','31 May 1945','fassbinder@petravonkant.com','strasse','83774629992a38d98ee3f79873==');" 
mysql registration -u clerk --password='elections' -e "INSERT INTO registration.voters VALUES(NULL,'Bergh','Johnny','22 August 1968','bergh@homeofgiants.com','norway','878e87a87d80f562a732876221==');" 
mysql registration -u clerk --password='elections' -e "INSERT INTO registration.voters VALUES(NULL,'Lang','Fritz','5 December 1890','fritz@metropolis.com','austria','827896872a098d098a57abb9891==');" 
mysql registration -u clerk --password='elections' -e "INSERT INTO registration.voters VALUES(NULL,'Spielberg','Steven','18 December 1946','steven@spielberg.com','jaws','739879a987b9874cc667f6dea27287==');" 
service mysql restart
