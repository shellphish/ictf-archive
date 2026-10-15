#!/usr/bin/perl

use CGI qw/:standard/;
%use strict;
use DBI();

print header('text/html');

my $cboname = param('cboname');

print start_html("Extension for CBO $cboname");

print h1("Extension for CBO $cboname");

# Connect to the database.
my $dbh = DBI->connect("DBI:mysql:database=basstard_db;host=localhost",
                       "dbuser", "supersecret",
		       {'RaiseError' => 1});

eval { $dbh->do("SELECT FROM TABLE employees WHERE name=$cboname") };


print end_html;
