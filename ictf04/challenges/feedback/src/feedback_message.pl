#!/usr/bin/perl

use CGI qw/:standard/;

### Get query parameters and check for empty entries

$name = param('name');
$candidate = param('candidate');
$msg = param('comment');

if ($name eq "") {
    $name = "Anonymous";
}

if ($msg eq "") {
    $msg = "No message";
}

### Add message to guestbook

$failed = 0;

if (-e "./guestbook.txt") { 
  open(FILE, ">> ./guestbook.txt") or $failed = 1; 
  if ($failed == 0) {
    print(FILE "<p><b>$name</b> wrote:\n<pre>\n$msg\n</pre>\n</p>\n\n");
    close(FILE);
  }
}
else {
  $failed = 2;
}


### HTML page header

print "Content-type: text/html\n\n";
print "<html>\n  <head>\n    <title>The Bass Tard Corporation</title>\n";
print "    <link href=\"/basstard.css\" rel=\"stylesheet\" type=\"text/css\">\n  </head>\n";
print "  <body>\n    <div class=\"main\">\n";
print "      <div class=\"header\">\n        <h1>The Bass Tard Corporation</h1>\n      </div>\n";
print "      <div class=\"menu\">\n        <div class=menu_top> Site </div>\n";
print "        <div class=menu_sub> <a href=\"/index.html\"> Main </a> </div>\n";
print "        <div class=menu_top> Company </div>\n";
print "        <div class=menu_sub> <a href=\"/history.html\"> History </a> </div>\n";
print "        <div class=menu_sub> <a href=\"/financial.html\"> Profile </a> </div>\n";
print "        <div class=menu_sub> <a href=\"/feedback.html\">Feedback</a> </div>\n";
print "        <div class=menu_sub> <a href=\"/cgi-bin/guestbook.pl\">Guestbook</a> </div>\n";
print "        <div class=menu_sub> <a href=\"/guestbook_admin.html\">Admin</a> </div>\n";
print "        <div class=menu_top> Contact </div>\n";
print "        <div class=menu_sub> <a href=\"/contact.html\">Find</a> </div>\n";
print "        <div class=menu_sub> <a href=\"/change.html\">Admin </a></div>\n";
print "        <div class=menu_top> Help </div>\n";
print "        <div class=menu_sub> <a href=\"http://128.111.48.5:8080/support/search\">Search</a> </div>\n";
print "        <div class=menu_sub> <a href=\"http://128.111.48.5:8080/support/admin\">Admin</a> </div>\n";
print "      </div>\n";
print "      <div class=\"content\">\n";

### End header

if ($failed == 0) {

    print "<h2>Feedback received</h2>\n";
    print "<p>Your feedback has been received and will be soon screened for content</p>";
    print "<p>If you wrote anything bad about us, your comments will be destroyed (and we will probably break your legs, too)</p>";
    print "<p>For now, you can view your comments in our <a href=\"/cgi-bin/guestbook.pl\">Guestbook</a>.</p>";

} else {

    print "<h2>Saving message failed</h2>\n";

    if ($failed == 1) {
	print "<p>Cannot open file guestbook.txt</p>\n";
    }
    else {
	print "<p>File guestbook.txt not found</p>\n";
    }
}


### HTML page footer

print "      </div>\n    </div>\n";
print "    <div class=\"footer\">\n      (C) 2003, The Bass Tard Corporation\n    </div>\n";
print "  </body>\n</html>\n";

### End footer
