#!/usr/bin/perl -W



### HTML page header

print "Content-type: text/html\n\n";
system ("cat ./templates/header.html");

### End header

print "<h2>Guestbook</h2>\n";
system("cat ./guestbook.txt");


### HTML page footer

system ("cat ./templates/footer.html");

### End footer

