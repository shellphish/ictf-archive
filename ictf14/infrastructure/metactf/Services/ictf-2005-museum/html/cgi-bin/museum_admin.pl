#!/usr/bin/perl

use CGI qw/:standard/;
$failed = 0; 
### Get query parameters 

$first = param('first');
$last = param('last');
$password = param('password');

### HTML page header


print "Content-type: text/html\n";


print "\n";

print "<html>\n  <head>\n    <title>SPAM Museum Administrator Interface</title>\n";
print "    <link href=\"/spam.css\" rel=\"stylesheet\" type=\"text/css\">\n  </head>\n";
print "  <body>\n";
print "      <div class=\"banner\">\n        <h1>SPAM Search Results</h1>\n      </div>\n";
print "      <div class=\"main\">\n";

if (($first eq "") || ($last eq "") || (! $password eq "unbreakable")) {
  print "<p>Could not understand user name or wrong password!!</p>";
}
else {
  system "cat ./museum_ideas/${first}.${last}";
}
### HTML page footer

print "      </div>\n";
print "    <div class=\"footer\">\n <hr />Supported by the <a href=\"/aqs/\">Association for Quality SPAM</a></div>\n";
print "  </body>\n</html>\n";

### End footer
