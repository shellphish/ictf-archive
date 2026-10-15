-- Start mysql with
-- myswld_safe &
-- Load database with 
-- mysql -u root -p < mysql_init.sql

DROP DATABASE IF EXISTS registration;
CREATE DATABASE registration;

DROP TABLE IF EXISTS registration.voters;
CREATE TABLE registration.voters (
	last VARCHAR(200) NOT NULL,
        first VARCHAR(200) NOT NULL,
	dob VARCHAR(200) NOT NULL,
	email VARCHAR(200) NOT NULL,
	password VARCHAR(200) NOT NULL,
	wwid VARCHAR(200) NOT NULL UNIQUE PRIMARY KEY);

GRANT SELECT, INSERT, UPDATE ON registration.voters 
TO clerk@localhost IDENTIFIED BY 'elections';

INSERT INTO registration.voters VALUES (
	'Fellini',
	'Federico',
	'Jan 20, 1920',
	'fellini@amarcord.it',
	'volpina',
	'73bb828929783a987d287e4c8==');

INSERT INTO registration.voters VALUES (
	'Fassbinder',
	'Rainer Werner',
	'31 May 1945',
	'fassbinder@petravonkant.com',
	'strasse',
	'83774629992a38d98ee3f79873==');

INSERT INTO registration.voters VALUES (
	'Bergh',
	'Johnny',
	'22 August 1968',
	'bergh@homeofgiants.com',
	'norway',
	'878e87a87d80f562a732876221==');

INSERT INTO registration.voters VALUES (
	'Lang',
	'Fritz',
	'5 December 1890',
	'fritz@metropolis.com',
	'austria',
	'827896872a098d098a57abb9891==');

INSERT INTO registration.voters VALUES (
	'Spielberg',
	'Steven',
	'18 December 1946',
	'steven@spielberg.com',
	'jaws',
	'739879a987b9874cc667f6dea27287==');
