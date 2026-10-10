drop table if exists users;


create table users (
	id MEDIUMINT NOT NULL AUTO_INCREMENT,
	username varchar(32),
	password varchar(32),
	role ENUM('client', 'counselor'),
	firstname varchar(32),
	lastname varchar(32),
	email varchar(128),
	counselor varchar(32),
	private_info varchar(128),
	description TEXT,
	PRIMARY KEY (id)
);
