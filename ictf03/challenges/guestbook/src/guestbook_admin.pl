#!/usr/bin/perl

use CGI qw(:standard);
use Digest::MD5 qw(md5_hex);

### Get query parameters 

$login = param('login');
$pass = param('password');
$query = new CGI;


### Perform credential checks

$authenticated = 0;

$digest = md5_hex($pass);
if (($login eq "admin") && ($digest eq "##GUESTBOOK_ADMIN_PASS##")) {
    $authenticated = 1;
}


### HTML page header

print "Content-type: text/html\n\n";
system ("cat ./templates/header.html");

### End header

if ($authenticated == 1) {

    print "<h2>Guestbook Admin</h2>\n";

    print "<form action=\"/cgi-bin/save_messages_admin.pl\" method=\"post\">\n";
    print "   <p><input type=\"hidden\" name=\"login\" value=\"$login\"></p>\n";
    print "   <p><input type=\"hidden\" name=\"password\" value=\"$pass\"></p>\n";
    print "   <p><textarea name=\"messages\" rows=\"20\" cols=\"80\">\n";
    system ("cat ./guestbook.txt");
    print "   </textarea></p>\n";
    print "   <p><input type=\"submit\" value=\"Commit Changes\"></p>\n";
    print "</form>\n";

} else {
    print "<h2>Access Denied</h2>\n";
}


### HTML page footer

system ("cat ./templates/footer.html");

### End footer
