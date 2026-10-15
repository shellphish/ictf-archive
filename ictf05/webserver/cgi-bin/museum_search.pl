#!/usr/bin/perl

use CGI qw/:standard/;
$failed = 0; 
### Get query parameters 

$keyword = param('keyword');

### HTML page header

print "Content-type: text/html\n";


print "\n";

print "<html>\n  <head>\n    <title>SPAM Search Results</title>\n";
print "    <link href=\"/spam.css\" rel=\"stylesheet\" type=\"text/css\">\n  </head>\n";
print "  <body>\n";
print "      <div class=\"banner\">\n        <h1>SPAM Search Results</h1>\n      </div>\n";
print "      <div class=\"main\">\n";
print "Using keyword $keyword...";

if (($keyword eq "") || ($keyword =~ /.*[;].*/)) {
  print "<p>Could not understand your keyword!!</p>";
  print "<p>It might be empty or contain illegal characters!!</p>";
}
else {
  while (<./museum_spam/*>) {
    $result = system "grep -i $keyword $_ > /dev/null";
    if ($result == 0)	{
      print "<hr />";
      system "cat $_";
    }
  }
}

### HTML page footer

print "      </div>\n";
print "    <div class=\"footer\">\n <hr />Supported by the <a href=\"/aqs/\">Association for Quality SPAM</a></div>\n";
print "  </body>\n</html>\n";

### End footer
