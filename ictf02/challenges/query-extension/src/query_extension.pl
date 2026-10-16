#!/usr/bin/perl

use CGI qw/:standard/;
# use strict;
use DBI();


print header('text/html');

my $cboname = param('cboname');

print start_html("Extension for CBO $cboname");

print h1("Extension for CBO $cboname");

# Connect to the database.
my $dbh = DBI->connect("DBI:mysql:database=corpdb;host=saa.basstard.com",
                       "dbuser", "dbsecret",
		       {'RaiseError' => 1});

$sth = $dbh->prepare("SELECT first, extension FROM Employees WHERE last = '$cboname';");
$sth->execute();

while (@result = $sth->fetchrow_array()) {
    print "<br>\n";
    print join (" ", @result), "\n";
}

# eval { $dbh->do("SELECT * FROM Employees WHERE last = 'Schmidt';") };


foreach $elem (@result) {
    print "## $elem\n";
}

print end_html;
