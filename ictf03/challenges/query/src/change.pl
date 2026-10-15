#!/usr/bin/perl 

use CGI qw/:standard/;
use DBI();
use Digest::MD5 qw(md5_hex);

### get all query parameters 

# make a new CGI query object
$query = new CGI;

# get all parameter names  
@paras = $query->param;

# copy values into paramter names
foreach $para (@paras) { 
    $$para = $query->param($para);
} 

# sanitize all possible SQL arguments

$last =~ s/[^a-zA-Z0-9]//g;
$first =~ s/[^a-zA-Z0-9]//g;
$ext =~ s/[^a-zA-Z0-9]//g;
$id =~ s/[^a-zA-Z0-9]//g;

### check for correct credentials

$digest = md5_hex($password);
if (($login eq "admin") && ($digest eq "##QUERY_ADMIN_PASS##")) {
    $authenticated = 1;
}

### Connect to the database and do the lookup

if ($authenticated == 1) {

    $failed = 0;

    if (($last eq "") || ($first eq "")) {
	$failed = 1;
    }

    if ($failed == 0) {
	$dbh = DBI->connect("DBI:Pg:dbname=querydb","queryuser", "##QUERY_DB_PASS##") or $failed = 2;	
    }
    
    if ($failed == 0) {
	if ($id ne "") {
	    $sth = $dbh->prepare("UPDATE employees SET id='$id' WHERE last='$last' AND first='$first';");
	    $result = $sth->execute() or $failed = 3;
	}
	
	if ($ext ne "") {
	    $sth = $dbh->prepare("UPDATE employees SET ext='$ext' WHERE last='$last' AND first='$first';");
	    $result = $sth->execute() or $failed = 3;
	}
    }
}


### HTML page header

print "Content-type: text/html\n\n";
system ("cat ./templates/header.html");

### End header


if ($authenticated == 1) {

    if ($failed != 0) {

	print "<h2>Update Failed</h2>";

	if ($failed == 1) {
	    print "<p>Last and first name must not empty</p>\n";
	}
	elsif ($failed == 2) {
	    print "<p>Cannot connect to database</p>\n";
	}
	elsif ($failed == 3) {
	    print "<p>Cannot execute query</p>\n";
	}
	elsif ($failed == 4) {
	    print "<p>\"$first $last\" not found in database</p>\n";
	} 
    } else {
	print "<h2>Update Successful</h2>";

	if ($result == 0) {
	    print "<p>No row has been changed</p>\n";
	}
	else {
	    print "<p>$result row(s) have been changed</p>\n";
	}
        print "<p><b>Note:</b> setting the extension to the existing value results in no changed rows</p>\n";
    }
} else {
    print "<h2>Access Denied</h2>";
}


### HTML page footer

system ("cat ./templates/footer.html");

### End footer
