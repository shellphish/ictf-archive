#!/usr/bin/perl

use CGI qw/:standard/;
use DBI;

$testing = 0;

print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>Voter Data Review</title>\n";
print "    <link href=\"/vote.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"banner\">\n";
print "      <h1>Voter Data Review</h1>\n";
print "    </div>\n";
print "    <div class=\"main\">\n";

open(scripts, "checkinput.js") or do {
  print "<p>There is a problem loading the server definitions.</p>\n";
  print "<p>Please contact the Administrator.</p>\n";
  goto TAIL;
};

while (<scripts>) {
  print "$_";
};

if ($testing == 0) {
  $wwid = param('wwid');
  $wwid =~ s/[^a-zA-Z0-9,\-=]//g;
  $password = param('password');
  $password =~ s/[^a-zA-Z0-9']//g;
  $debug = param('debug');
}

if ($testing == 1) {
  print "<!-- Working on test data -->\n";
  $wwid = "827896872a098d098a57abb9891";
  $password = "zanna";
}

if ($wwid eq "") {
  print "<p>You have provided an empty World-Wide ID.</p>\n";
  print "<p>You cannot access your data.</p>\n";
  goto TAIL;
}

if ($password eq "") {
  print "<p>You have provided an empty password.</p>\n";
  print "<p>You cannot access your data.</p>\n";
  goto TAIL;
}

my $dbh = DBI->connect("DBI:mysql:database=registration;host=localhost","clerk", "elections") or do {
  print "<p>We are experiencing a database problem.</p>\n";
  print "<p>Please try to connect at another time.</p>\n";
  print "<p>Sorry for the inconvenience</p>\n";
  goto TAIL;
};

my $query = "SELECT * FROM registration.voters WHERE wwid = '$wwid' AND password = '$password';";

if ($testing || $debug) {
  printf "<p><tt>Executing: $query</tt></p>\n";
}

my $sth = $dbh->prepare($query);
$sth->execute() or do {
  print "<p>At the moment, we are not able to execute database queries.</p>\n";
  print "<p>Please try to connect at another time.</p>\n";
  print "<p>Sorry for the inconvenience.</p>\n";
  goto TAIL;
};

if ($sth->rows == 0) {
  print "<p>You provided the wrong World-Wide ID or password.</p>\n";
  print "<p>Please try again.</p>\n";
  goto TAIL;
}

if ($sth->rows > 1) {
  if ($testing || $debug) {
    print "<p>Results:</p>\n";
    print "<pre>\n";
    while (my $row = $sth->fetchrow_arrayref) {
      
      print join("\t", @$row),"\n";
    }
    print "</pre>\n";
  }

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

$last = $row->[0];
$first = $row->[1];
$dob = $row->[2];
$email = $row->[3];
$password = $row->[4];
$wwid = $row->[5];

print "<form name=\"update\" action=\"/cgi-bin/update.pl\" onsubmit=\"checkupdate()\" method=\"post\">\n";
print "<input type=\"hidden\" name=\"first\" value=\"$first\">\n";
print "<input type=\"hidden\" name=\"last\" value=\"$last\">\n";
print "<input type=\"hidden\" name=\"dob\" value=\"$dob\">\n";
print "<input type=\"hidden\" name=\"wwid\" value=\"$wwid\">\n";
print "<input type=\"hidden\" name=\"email\" value=\"$email\">\n";
print "<input type=\"hidden\" name=\"password\" value=\"$password\">\n";
print "<p><table summary=\"update\">\n";
print "<tr><td>First:</td><td><input type=\"text\" name=\"newfirst\" value=\"$first\"></td></tr>\n";
print "<tr><td>Last:</td><td><input type=\"text\" name=\"newlast\" value=\"$last\"></td></tr>\n";
print "<tr><td>Date Of Birth:</td><td><input type=\"text\" name=\"newdob\" value=\"$dob\"></td></tr>\n";
print "<tr><td>World-Wide ID:</td><td><input type=\"text\" name=\"newwwid\" value=\"$wwid\"></td></tr>\n";
print "<tr><td>E-mail:</td><td><input type=\"text\" name=\"email\" value=\"$email\"></td></tr>\n";
print "<tr><td>Password:</td><td><input type=\"password\" name=\"newpassword\" value=\"$password\"></td></tr>\n";
print "<tr><td><input type=\"submit\" value=\"Update\"></td><td></td></tr></table>\n";
print "</form>\n";

TAIL: {
  print "    </div>\n";
  print "    <div class=\"footer\">\n";
  print "      <hr />\n";
  print "      <p>Administered by <a href=\"/diebald\">The Die-Bald Corporation</a></p>\n";
  print "    </div>\n";
  print "  </body>\n";
  print "</html>\n";
}
