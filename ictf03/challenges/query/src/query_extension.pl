#!/usr/bin/perl 

use CGI qw/:standard/;
use DBI();

### get name to lookup and sanitize input

$cboname = param('cboname');
$cboname =~ s/[^a-zA-Z]//g;


### Connect to the database and do the lookup

$failed = 0;

my $dbh = DBI->connect("DBI:Pg:dbname=querydb","queryuser", "##QUERY_DB_PASS##") or $failed = 1;

if ($failed == 0) {

    if ($cboname eq "") {
	$sth = $dbh->prepare("SELECT * FROM employees ORDER BY last;");
    } else {
	$sth = $dbh->prepare("SELECT * FROM employees WHERE last = '$cboname' ORDER BY last;");
    }

    $sth->execute() or $failed = 2;
}

### HTML page header

print "Content-type: text/html\n\n";
system ("cat ./templates/header.html");

### End header



if ($failed != 0) {

    print "<h2>Lookup failed</h2>";

    if ($failed == 1) {
	print "<p>Cannot connect to database</p>\n";
    }
    else {
	print "<p>Cannot execute query</p>\n";
    }
} else {

    print "<h2>Employees</h2>";
    print "<p>We found the following extensions:</p>\n";
    print "<p><table cellpadding=\"5px\" border=\"1px\">\n";
    print "  <tr><td><b>Last Name</b></td><td><b>First Name</b></td><td><b>ID</b></td><td><b>Extension</b></td></tr>\n";   

    while (@result = $sth->fetchrow_array()) {
	print "  <tr><td>$result[0]</td><td>$result[1]</td><td>$result[2]</td><td>$result[3]</td></tr>\n";
    }
    
    print "</table></p>\n";
}



### HTML page footer

system ("cat ./templates/footer.html");

### End footer
