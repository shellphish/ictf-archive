drop database Contributions;
create database Contributions;
GRANT ALL PRIVILEGES ON Contributions.* TO 'contribute'@'localhost' identified by 'changeme';
use Contributions;
create table contributors ( id int(32), name varchar(256), amount int(32), address varchar(256), ccn varchar(32) );

