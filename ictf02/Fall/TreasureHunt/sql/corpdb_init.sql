DROP DATABASE IF EXISTS corpdb;
CREATE DATABASE corpdb;
#USE viewer_devel;

DROP TABLE IF EXISTS Employees;
CREATE TABLE Employees ( last VARCHAR(255) NOT NULL,
		         first VARCHAR(255) NOT NULL,
			 ssn VARCHAR(255) NOT NULL,
                         descr VARCHAR(255) NOT NULL,
			 extension VARCHAR(255) NOT NULL,
		         PRIMARY KEY (ssn) ); 

DROP TABLE IF EXISTS Payroll;
CREATE TABLE Payroll ( ssn VARCHAR(255) NOT NULL,
		       cc VARCHAR(255) NOT NULL,
		       abi VARCHAR(255) NOT NULL,
		       cab VARCHAR(255) NOT NULL,
		       routing VARCHAR(255) NOT NULL,
                       PRIMARY KEY (ssn) );

# Add entries




