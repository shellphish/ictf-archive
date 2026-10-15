#!/usr/bin/perl

use CGI qw/:standard/;
use DBI;

$testing = 0;

print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>Voter Registration Request</title>\n";
print "    <link href=\"/vote.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"banner\">\n";
print "      <h1>Voter Registration Request</h1>\n";
print "    </div>\n";
print "    <div class=\"main\">\n";

$testing = 0;

if ($testing == 0) {
  $last = param('last');
  $last =~ s/[^a-zA-Z0-9\-\s]//g;
  $first = param('first');
  $first =~ s/[^a-zA-Z0-9\-\s]//g;
  $dob = param('dob');
  $dob =~ s/[^a-zA-Z0-9,\-\s]//g;
  $wwid = param('wwid');
  $wwid =~ s/[^a-zA-Z0-9,\-=]//g;
  $email = param('email');
  $email =~ s/[^a-zA-Z0-9@\.\-]//g;
  $password = param('password');
  $password =~ s/[^a-zA-Z0-9]//g;
  $debug = param('debug');
}

if ($testing == 1) {
  print "<!-- Working on test data -->\n";
  $last = "Zanardi";
  $first = "Massimo";
  $dob = "February 29 1968";
  $wwid = "827896872a098d098a57abb9891";
  $email = "z4n4rd1\@pazienza.it";
  $password = "zanna";
}

if ($wwid eq "") {
  print "<p>You have provided an empty World-Wide ID.</p>\n";
  print "<p>Your registration cannot be completed.</p>\n";
  goto TAIL;
}

my $dbh = DBI->connect("DBI:mysql:database=registration;host=localhost","clerk", "elections") or do {
  print "<p>We are experiencing a database problem.</p>\n";
  print "<p>Please try to connect at another time.</p>\n";
  print "<p>Sorry for the inconvenience</p>\n";
  goto TAIL;
};

my $query = "SELECT * FROM registration.voters WHERE wwid = '$wwid';";
if ($testing || $debug) {
  printf "<p><tt>Executing: $query</tt></p>\n";
}

my $sth = $dbh->prepare($query);
$sth->execute() or do {
  print "<p>At the moment, we are not able to execute database queries.</p>\n";
  print "<p>Please try to connect at another time.</p>\n";
  print "<p>Sorry for the inconvenience</p>\n";
  goto TAIL;
};

if ($testing || $debug) {
  print "<p>Results:</p>\n";
  print "<pre>\n";
  while (my $row = $sth->fetchrow_arrayref) {
    
    print join("\t", @$row),"\n";
  }
  print "</pre>\n";
}
if ($sth->rows > 0) {
  print "<p>A user with the provided World-Wide ID already exists.</p>\n";
  print "<p>Please check your data and resubmit your registration.</p>\n";
  print "<p>Sorry for the inconvenience</p>\n";
  goto TAIL;
}

$query = "INSERT INTO registration.voters VALUES ('$last','$first','$dob','$email','$password','$wwid');";

if ($testing || $debug) {
  printf "<p><tt>Executing: $query</tt></p>\n";
}

$sth = $dbh->prepare($query);
$sth->execute() or do {
  print "<p>At the moment, we are not able to insert your data.</p>\n";
  print "<p>Please try to connect at another time.</p>\n";
  print "<p>Sorry for the inconvenience</p>\n";
  goto TAIL;
};

print "<p>Registration successful!</p>\n";
print "<p>You are now registered to vote.</p>\n";
print "<p>You can review your voter registration at any time using the registration web page.</p>\n";

TAIL: {
  print "    </div>\n";
  print "    <div class=\"footer\">\n";
  print "      <hr />\n";
  print "      <p>Administered by <a href=\"/diebald\">The Die-Bald Corporation</a></p>\n";
  print "    </div>\n";
  print "  </body>\n";
  print "</html>\n";
}
