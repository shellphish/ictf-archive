#!/usr/bin/perl

use CGI qw/:standard/;

### Get query parameters and check for empty entries
# make a new CGI query object
$query = new CGI;

# get all parameter names  
@paras = $query->param;

# copy values into paramter names
foreach $para (@paras) {
  $$para = $query->param($para);
}

if ($last eq "") {
    $last = "Anonymous";
}

if ($first eq "") {
    $first = "Anonymous";
}

if ($comment eq "") {
    $comment = "No message";
}

if ($private eq "") {
    $private = "no";
}


### HTML page header
print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>The Bass Tard Corporation - Feedback Submission</title>\n";
print "    <meta name=\"Author\" content=\"Massimo Zanardi\">";
print "    <link href=\"/basstard.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"main\">\n";
print "      <div class=\"header\">\n";
print "        <h1>The Bass Tard Corporation</h1>\n";
print "      </div>\n";
print "      <!--<div class=\"menu\"></div>-->\n";
print "      <div class=\"content\">\n";
### End header

$failed = 0;

### Add message to guestbook

# Check if it is a one-liner
$lines = `echo \"$comment\" | wc -l`;
if ($lines != 1) {
  $failed = 3;
}

if ($failed == 0) {
  if (-e "data/guestbook.txt") {
    open(FILE, ">> data/guestbook.txt") or $failed = 1;
   if ($failed == 0) {
      print FILE "<p><b>$first $last</b>";
      if ($private eq "yes") {
	print FILE " (PRIVATELY)";
      }
      print FILE " wrote: <pre>$comment</pre></p>\n";
      close(FILE);
    }
  }
  else {
    $failed = 2;
  }
}

if ($failed == 0) {
  
  print "<h2>Feedback received</h2>\n";
  print "<p>Your feedback has been received and will be soon screened for content.</p>";
  print "<p>If you wrote anything bad about us, your comments will be destroyed (and we will probably break your legs, too).</p>";
  print "<p>For now, you can view your comments (if public) in our <a href=\"/guestbook/cgi-bin/guestbook.pl\">Guestbook</a>.</p>";
} 
else {
  
  print "<h2>Saving message failed (error: $failed)</h2>\n";
  
  if ($failed == 1) {
    print "<p>Cannot open Guestbook file</p>\n";
  }
  elsif (${failed} == 2) {
    print "<p>Guestbook file not found</p>\n";
  }
  elsif (${failed} == 3) {
    print "<p>Your comment must be on just one line</p>\n";
  }
  else {
    print "<p>Generic error,sucka!</p>\n";
  }
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
