#!/usr/bin/perl

use CGI qw/:standard/;
use DBI;

$testing = 0;

print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>Voter Data Change Request</title>\n";
print "    <link href=\"/vote.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"banner\">\n";
print "      <h1>Voter Data Change Request</h1>\n";
print "    </div>\n";
print "    <div class=\"main\">\n";

if ($testing == 0) {
  $last = param('last');
  $newlast = param('newlast');
  $first = param('first');
  $newfirst = param('newfirst');
  $dob = param('dob');
  $newdob = param('newdob');
  $wwid = param('wwid');
  $newwwid = param('newwwid');
  $email = param('email');
  $newemail = param('newemail');
  $password = param('password');
  $newpassword = param('newpassword');
  $debug = param('debug');
}

if ($testing == 1) {
  print "<!-- Working on test data -->\n";
  $last = "Zanardi";
  $newlast = "Zanardi";
  $first = "Massimo";
  $newfirst = "Massimo";
  $dob = "February 29 1968";
  $newdob = "February 29 1968";
  $wwid = "827896872a098d098a57abb9891";
  $newwwid = "827896872a098d098a57abb9891";
  $email = "z4n4rd1\@pazienza.it";
  $newemail = "z4n4rd1\@pazienza.it";
  $password = "zinna";
  $newpassword = "zenna";
}

if ($wwid eq "") {
  print "<p>You have provided an empty World-Wide ID.</p>\n";
  print "<p>You cannot update your data.</p>\n";
  goto TAIL;
}

if ($password eq "") {
  print "<p>You have provided an empty password.</p>\n";
  print "<p>Your cannot update your data.</p>\n";
  goto TAIL;
}

my $dbh = DBI->connect("DBI:mysql:database=registration;host=localhost","clerk", "elections") or do {
  print "<p>We are experiencing a database problem.</p>\n";
  print "<p>Please try to connect at another time.</p>\n";
  print "<p>Sorry for the inconvenience</p>\n";
  goto TAIL;
};

my $query = "SELECT * FROM registration.voters WHERE wwid = '$wwid' and password = '$password';";
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

if ($sth->rows == 0) {
  print "<p>You provided the wrong World-Wide ID or password.</p>\n";
  print "<p>Please try again.</p>\n";
  goto TAIL;
}

if ($sth->rows > 1) {

  print "<p>The database contains multiple users with the same World-Wide ID and  password.</p>\n";
  print "<p>This should not happen. Please contact the Administrator.</p>\n";

  goto TAIL;
}

my $row = $sth->fetchrow_arrayref;

if ($testing || $debug) {
  print "<p>Results:</p>\n";
  print "<pre>\n";
  print join("\t", @$row),"\n";
  print "</pre>\n";
}

if ($newpassword eq "") {
  $newpassword = $password;
}
if ($newfirst eq "") {
  $newfirst = $first;
}
if ($newlast eq "") {
  $newlast = $last;
}
if ($newemail eq "") {
  $newemail = $email;
}
if ($newdob eq "") {
  $newdob = $dob;
}
if ($newwwid eq "") {
  $newwid = $wwid;
}

$query = "UPDATE registration.voters SET last='$newlast', first='$newfirst', dob='$newdob', email='$newemail', password='$newpassword', wwid='$newwwid' WHERE wwid = '$wwid';";

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

print "<p>Your personal information has been updated!</p>\n";

TAIL: {
  print "    </div>\n";
  print "    <div class=\"footer\">\n";
  print "      <hr />\n";
  print "      <p>Administered by <a href=\"/diebald\">The Die-Bald Corporation</a></p>\n";
  print "    </div>\n";
  print "  </body>\n";
  print "</html>\n";
}
