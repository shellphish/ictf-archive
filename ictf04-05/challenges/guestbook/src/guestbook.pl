#!/usr/bin/perl
use CGI qw/:standard/;
$guestbook = "./guestbook.txt";
$keyword = "PRIVATELY";

$query = new CGI;

# get all parameter names  
@paras = $query->param;

# copy values into paramater names
foreach $para (@paras) {
  $$para = $query->param($para);
}

### HTML page header

print "Content-type: text/html\n\n";
print "<html>\n";
print "  <head>\n";
print "    <title>The Bass Tard Corporation - Guestbook</title>\n";
print "    <meta name=\"Author\" content=\"Massimo Zanardi\">\n";
print "    <link href=\"/basstard.css\" rel=\"stylesheet\" type=\"text/css\">\n";
print "  </head>\n";
print "  <body>\n";
print "    <div class=\"main\">\n";
print "      <div class=\"header\">\n";
print "        <h1>The Bass Tard Corporation</h1>\n";
print "      </div>\n";
print "      <div class=\"content\">\n";

### End header

print "<h2>Guestbook</h2>\n";
if (${user}) {
  $command = "grep ${user} ${guestbook}";
  $usercomments = `${command}`;
}
else {
  $command = "cat ${guestbook} | grep -v ${keyword}";
  $usercomments = `${command}`;
}

print $usercomments;

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


