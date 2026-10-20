#!/usr/bin/perl

use CGI qw/:standard/;
use DBI();

$init_file = "/usr/ctf/contact/init.pl";
$identity = "id";

# make a new CGI query object
$query = new CGI;

# get all parameter names  
@paras = $query->param;

# copy values into paramter names
foreach $para (@paras) {
  $$para = $query->param($para);
}

### HTML page header
print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>The Bass Tard Corporation - Contact Info</title>\n";
print "    <meta name=\"Author\" content=\"Massimo Zanardi\">\n";
print "    <link href=\"/contact/basstard.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"main\">\n";
print "      <div class=\"header\">\n";
print "        <h1>The Bass Tard Corporation</h1>\n";
print "      </div>\n";
print "      <!-- <div class=\"menu\"></div> -->\n";
print "      <div class=\"content\">\n";

### End header

if (-e ${init_file}) {
  eval `cat ${init_file}`;
}

$cboname =~ s/[^a-zA-Z]//g;

### Connect to the database and do the lookup

$failed = 0;

my $dbh = DBI->connect("DBI:mysql:database=corpdb;host=localhost","corpdbuser", "basstard") or $failed = 1;

if ($failed == 0) {
    $sth = $dbh->prepare("SELECT * FROM employees WHERE last = '$cboname' ORDER BY last;");
    $sth->execute() or $failed = 2;
}

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
    print "  <tr><td><b>Last Name</b></td><td><b>First Name</b></td><td><b>Extension</b></td></tr>\n";   

    while (@result = $sth->fetchrow_array()) {
	print "  <tr><td>$result[0]</td><td>$result[1]</td><td>$result[2]</td></tr>\n";
    }
    
    print "</table></p>\n";
}

### HTML page footer

print "      </div>\n";
print "    </div>\n";
print "    <div class=\"footer\">\n";
if ($debug ne "") {
  print "<pre>\n";
  print `${identity}`;
  print "</pre>\n";
}
print "      (C) 2005, The Bass Tard Corporation\n";
print "    </div>\n";
print "  </body>\n";
print "</html>\n";

### End footer
