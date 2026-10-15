#!/usr/bin/perl

use CGI qw/:standard/;
use Digest::MD5 qw(md5_hex);

### Get query parameters 

$login = param('login');
$pass = param('password');
$msgs = param('messages');

$query = new CGI;


### Perform credential checks

$authenticated = 0;

$digest = md5_hex($pass);
if (($login eq "admin") && ($digest eq "##GUESTBOOK_ADMIN_PASS##")) {
    $authenticated = 1;
}

if ($authenticated == 1)
{
    open(FILE, "> ./guestbook.txt") or $failed = 1;
    if ($failed == 0) {
	print(FILE $msgs);
	close(FILE);
    }
}


### HTML page header

print "Content-type: text/html\n\n";
system ("cat ./templates/header.html");

### End header

if (($authenticated == 0) || ($failed == 1)) {

    print "<h2>Operation failed</h2>\n";

    if ($authenticated == 0) {
	print "<p>Invalid credentials</p>";
    }
    if ($failed == 1) {
	print "<p>Cannot access guestbook.txt</p>";
    }
} else {
    print "<h2>Guestbook changed</h2>\n";

    print "<p>Your changes have been commited. Click <a href=\"/cgi-bin/guestbook.pl\">here</a> to see the results.</p>";
}


### HTML page footer

system ("cat ./templates/footer.html");

### End footer
