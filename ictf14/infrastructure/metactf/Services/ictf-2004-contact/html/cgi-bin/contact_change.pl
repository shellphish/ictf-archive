#!/usr/bin/perl 

use CGI qw/:standard/;
use DBI();
use Digest::MD5 qw(md5_base64);


### get all query parameters 

# make a new CGI query object
$query = new CGI;

# get all parameter names  
@paras = $query->param;

# copy values into paramter names
foreach $para (@paras) {
  $$para = $query->param($para);
}

### check for correct credentials

### HTML page header

print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>The Bass Tard Corporation - CBO Update Information</title>\n";
print "    <meta name=\"Author\" content=\"Massimo Zanardi\">";
print "    <link href=\"/contact/basstard.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"main\">\n";
print "      <div class=\"header\">\n";
print "        <h1>The Bass Tard Corporation</h1>\n";
print "      </div>\n";
print "      <!--<div class=\"menu\"></div>-->\n";
print "      <div class=\"content\">\n";

### End header

$digest = md5_base64($password);

if (($login eq "admin") && ($digest eq "M/cyeOOXzHvO4LXQx/lLuA")) {
  $authenticated = 1;
}

### Connect to the database and do the lookup

if ($authenticated == 1) {
  
  $failed = 0;

  if (($last eq "") || ($first eq "") || ($ext eq "")) {
    $failed = 1;
  }
  
  if ($failed == 0) {
    $dbh = DBI->connect("DBI:mysql:database=corpdb;host=localhost","corpdbuser", "basstard") or $failed = 2;
  }

  if ($failed == 0) {
    $sth = $dbh->prepare("SELECT * FROM employees WHERE last='$last' AND first='$first';");
    $result = $sth->execute() or $failed = 3;

    if ($result == 0)
      {
	$sth = $dbh->prepare("INSERT INTO employees (last, first, extension) VALUES ('$last', '$first', '$ext');");
	$newresult = $sth->execute() or $failed = 4;
      }
  }
    
  if ($failed == 0) {
    $sth = $dbh->prepare("UPDATE employees SET extension='$ext' WHERE last='$last' AND first='$first';");
    $result = $sth->execute() or $failed = 5;
  }
  
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
      print "<p>Cannot insert new values</p>\n";
    }
    elsif ($failed == 5) {
      print "<p>Cannot update values</p>\n";
    }
  } else {
    print "<h2>Update Successful</h2>";
  }
} else {
  print "<h2>Access Denied</h2>";
}


### HTML page footer

print "      </div>\n";
print "    </div>\n";
print "    <div class=\"footer\">\n";
if ($debug ne "") {
  print "<pre>\n";
  print `id`;
  print "</pre>\n";
}
print "      (C) 2005, The Bass Tard Corporation\n";
print "    </div>\n";
print "  </body>\n";
print "</html>\n";

### End footer
