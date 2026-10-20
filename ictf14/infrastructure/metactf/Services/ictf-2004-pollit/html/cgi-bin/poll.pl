#!/usr/bin/perl

use CGI qw/:standard/;
use DBI;

print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>To Poll, Or Not To Poll</title>\n";
print "    <link href=\"../un.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"banner\">\n";
print "      <h1>To Poll Or Not To Poll</h1>\n";
print "    </div>\n";
print "    <div class=\"main\">\n";

$testing = 0;

if ($testing == 0) {
  $username = param('username');
  $scope = param('scope');
  $op = param('op');
  $pollid = param('pollid');
  $schmidt = param('schmidt');
  $blitzkrieg = param('blitzkrieg');
  $stallone = param('stallone');
  $blix = param('blix');
  $schtrappe = param('schtrappe');
  $debug = param('debug');
  $poll = "$schmidt:$blitzkrieg:$stallone:$blix:$schtrappe";
}

if ($testing == 1) {
  print "<!-- Working on test data -->\n";
  $username = "bar";
  $scope = "global";
  $op = "compute";
  $pollid = "bbb63872876a98c98e98d99e9a";
  $poll = "10:20:5:30:25";
}

#if (!-e "polls") {
#  mkdir("polls") or do {
#    printf "<p>Cannot create poll database</p>\n";
#    goto TAIL;
#  }
#}

if ($scope eq "global") {
  do "global_func.pl";
} elsif ($scope eq "local") {
  # local scope
  do "local_func.pl";
} else {
  print "<p>Unknown poll scope $scope</p>\n";
  goto TAIL;
}

if ($op eq "upload") {
  ${pollid} =~ s,/,.,g;
  $pollfile = "polls/${username}.${pollid}";
  if ($debug)
    {
      print "<p><tt>Creating poll $pollid for user $username in file $pollfile</tt></p>\n";
    }
  open(FILE, "> $pollfile") or do {
    print "<p>Cannot write $username's poll file $pollid</p>\n";
    goto TAIL;
  };
  print FILE "$poll";
  close(FILE);
  print "<p>Poll $pollid saved.</p>\n";
  goto TAIL;
} 
elsif ($op eq "review") {
  ${pollid} =~ s,/,.,g;
  open(FILE, "< polls/$username.$pollid") or do {
    print "<p>Cannot read $username's poll file $pollid</p>\n";
    goto TAIL;
  };
  $poll = <FILE>;
  close(FILE);
  @thispoll = split(/:/, $poll);
  print "<h2>Review of poll $pollid</h2>\n";
   print "<table>\n";
  print "  <thead>\n";
  print "    <tr><td>Dottore Schmidt</td><td>Wolfgang Blitzkrieg</td><td>Matteo Stallone</td><td>Thor Blix</td><td>Jacques Schtrappe</td></tr>\n";
  print "  </thead>\n";
  print "  <tbody>\n";
  print "    <tr><td>$thispoll[0]</td><td>$thispoll[1]</td><td>$thispoll[2]</td><td>$thispoll[3]</td><td>$thispoll[4]</td></tr>\n";
  print "  </tbody>\n";
  print "</table>\n";
  goto TAIL;

} 
elsif ($op eq "compute") {
  if ($scope eq "global") {
    print "<h2>Global poll summary</h2>\n";
  }
  elsif ($scope eq "local") {
    print "<h2>Poll summary for user $username</h2>\n";
  }
  else {
    print "<p>Unknown poll scope $scope</p>\n";
    goto TAIL;
  }
  compute_poll();
}
else {
  print "<p>Unknown operation \"$op\" requested!</p>\n";
  goto TAIL;
}


TAIL: {
  print "<p>You can now return to the <a href=\"/ictf-2004-pollit/pollit.html\">poll page</a></p>\n";
  print "    </div>\n";
  print "    <div class=\"footer\">\n";
  print "      <hr />\n";
  print "      <p>Administered by <a href=\"/ictf-2004-pollit/index.html\">The Die-Bald Corporation</a></p>\n";
  print "    </div>\n";
  print "  </body>\n";
  print "</html>\n";
}
