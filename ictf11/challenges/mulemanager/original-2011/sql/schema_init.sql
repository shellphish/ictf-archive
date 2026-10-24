DROP DATABASE IF EXISTS mulemanager;
CREATE DATABASE mulemanager;
DROP TABLE IF EXISTS mulemanager.users;
CREATE TABLE mulemanager.users (
        username VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY,
        password VARCHAR(128) NOT NULL,
	email VARCHAR(128),
        first_name VARCHAR(128),
        last_name VARCHAR(128),
        phone VARCHAR(128),
        affiliation VARCHAR(128),
        address VARCHAR(128),
        city VARCHAR(128),
        state VARCHAR(128),
        zipcode VARCHAR(128),
        country VARCHAR(128),
        cookie VARCHAR(128) DEFAULT NULL);

DROP TABLE IF EXISTS mulemanager.groups;
CREATE TABLE mulemanager.groups (
        groupname VARCHAR(128) NOT NULL UNIQUE PRIMARY KEY);

DROP TABLE IF EXISTS mulemanager.groups_users;
CREATE TABLE mulemanager.groups_users (
        groupname VARCHAR(128) NOT NULL,
        username VARCHAR(128) NOT NULL);

DROP TABLE IF EXISTS mulemanager.endpoints;
CREATE TABLE mulemanager.endpoints (
        id INT UNSIGNED AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,
        username VARCHAR(128) NOT NULL,
        type VARCHAR(128) NOT NULL,
        address VARCHAR(128) NOT NULL,
	carrier VARCHAR(128),
	data VARCHAR(256));

DROP TABLE IF EXISTS mulemanager.accounts;
CREATE TABLE mulemanager.accounts (
        id INT UNSIGNED AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,
        username VARCHAR(128) NOT NULL,
        type VARCHAR(128) NOT NULL,
        routing VARCHAR(128) NOT NULL,
	number VARCHAR(128),
	amount INT,
	notes VARCHAR(256));
