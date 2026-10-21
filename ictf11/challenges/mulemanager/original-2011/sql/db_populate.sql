USE mulemanager;

INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) 
           VALUES ("admin", "admin", "Leet", "Admin", "admin@muleserver", "+1 (666) 666-6666", "Muleserver, Inc.", "Mule Road", "Mule City", "CA", "93891", "USA");

INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) 
           VALUES ("jdoe", "doedoe", "John", "Doe", "jdoe@foo.com", "+1 (805) 893-6151", "The Unknown, Inc.", "1288 Overlook Ln", "Santa Barbara", "CA", "93111", "USA");
INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) 
           VALUES ("jdee", "updog", "Jane", "Dee", "jdee@bar.com", "+1 (650) 112-1337", "The Missing L, Inc.", "Laguna Blanca Pl", "San Jose", "CA", "95014", "USA");
INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) 
           VALUES ("mark", "barfoo", "Mark", "Maglietta", "mark@barfoo.com", "+1 (811) 455-7232", "Mule Paradise", "Hacker Lane", "Goleta", "CA", "93117", "USA");
INSERT INTO users (username, password, first_name, last_name, email, phone, affiliation, address, city, state, zipcode, country) 
           VALUES ("bark", "bluetree", "Brian", "Ark", "bark@bark.com", "+1 (478) 911-6091", "Redneck Mules", "Banjo Street", "East Dublin", "GA", "31027", "USA");


INSERT INTO groups (groupname) 
           VALUES ("good mules");
INSERT INTO groups (groupname) 
           VALUES ("bad mules");

INSERT INTO groups_users (groupname, username) 
           VALUES ("good mules", "jdoe");
INSERT INTO groups_users (groupname, username) 
           VALUES ("good mules", "jdee");
INSERT INTO groups_users (groupname, username) 
           VALUES ("bad mules", "mark");
INSERT INTO groups_users (groupname, username) 
           VALUES ("bad mules", "bark");

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("jdoe", "sms", "+1 (805) 876-1172", "Verizon");

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("jdoe", "sms", "+1 (231) 981-3256", "Sprint");

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("jdoe", "email", "jdoe@foo.com", NULL);

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("jdee", "sms", "+1 (123) 432-7761", "Sprint");

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("jdee", "email", "jdee@gmail.com", NULL);

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("jdee", "email", "jane.dee@hotmail.com", NULL);
		
INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("mark", "sms", "+1 (805) 782-2522", "Verizon");

INSERT INTO endpoints (username, type, address, carrier)
           VALUES ("bark", "sms", "+1 (805) 771-1128", "Verizon");

