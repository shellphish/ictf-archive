#!/usr/bin/perl -W

use CGI qw/:standard/;

$failed = 0;

### HTML page header

print "Content-type: text/html\n\n";
print "<html>\n  <head>\n    <title>SPAM Submission Feedback!</title>\n";
print "    <link href=\"/spam.css\" rel=\"stylesheet\" type=\"text/css\">\n  </head>\n";
print "  <body>\n";
print "  <div class=\"banner\">\n        <h1>Thanks for tour SPAM sample!!</h1>\n      </div>\n";
print "  <div class=\"main\">\n";

### Get query parameters and check for empty entries

$last = param('last');
$first = param('first');
$idea = param('idea');

if ($last eq "") {
  $failed = 1;
}

if ($first eq "") {
  $failed = 1;
}

if ($idea eq "") {
  $failed = 1;
}

if ($failed == 1) {
  print "   <h2>Sorry, we could not include your idea!!</h2>\n";
} else {
  ### Add message to guestbook

  open(FILE, "> ./museum_ideas/${first}.${last}") or $failed = 1;
  if ($failed == 0) {
    print(FILE "$idea");
    close(FILE);
  }

  if ($failed == 0) {

    print "<h2>Your idea has been received!!</h2>\n";
    print "<p>Thanks for contributing to the wonderful Museum of SPAM!</p>";
    print "<p>Soon your idea will be reviewed and possibly included in the Museum's collection!!</p>";
    print "<p>For now, you can <a href=\"~museum/search.html\">search</a> our current SPAM Museum collection!!</p>";
    
  } else {

    print "<h2>Sorry, could not save your idea!!</h2>\n";
    
    print "<p>Cannot open file ${first}.${last}!</p>\n";
  }
}

### HTML page footer

print "     </div>\n    </div>\n";
print "   <div class=\"footer\">\n <hr />Supported by the <a href=\"/aqs\">Association for Quality SPAM</a>!    </div>\n";
print "  </body>\n</html>\n";

### End footer
