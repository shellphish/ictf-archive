#!/bin/bash

psql -e -d querydb -c "DROP TABLE employees;"
psql -e -d querydb -c "CREATE TABLE employees (first text, last text, id text, ext integer);"
psql -e -d querydb -c "INSERT INTO employees VALUES ('Bill', 'Gates', 'myflag', 1001);"
psql -e -d querydb -c "INSERT INTO employees VALUES ('Steve', 'Ballmer', '2e28c7a753d21765dbe4c2c4e9ccc7f6', 1002);"
psql -e -d querydb -c "INSERT INTO employees VALUES ('John', 'Fink', '106463e472f6cc4e4b5d42aa9f573a51', 1011);"
psql -e -d querydb -c "INSERT INTO employees VALUES ('Christopher', 'Schmidt', '78f0e5a0fa4dfd4c3a3f21cb86ae3f1a', 1012);"
psql -e -d querydb -c "INSERT INTO employees VALUES ('Brian', 'Black', '649bdf211c086fc5c674fcc77da1c0fb', 1013);"
psql -e -d querydb -c "INSERT INTO employees VALUES ('William', 'Blake', '611a440c4517879ff5506f54ba07d4bf', 1014);"
psql -e -d querydb -c "GRANT ALL ON employees TO queryuser;"



