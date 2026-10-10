#!/usr/bin/perl -W

use CGI qw(:standard);
use Digest::MD5 qw(md5_hex);

### Get query parameters and check for empty entries

$last = param('last');
$first = param('first');
$msg = param('comment');

if ($last eq "") {
    $last = "Anonymous";
}

if ($first eq "") {
    $first = "Anonymous";
}

if ($msg eq "") {
    $msg = "No message";
}



### Add message to guestbook

# create a unique message id

$msgid = md5_hex(`date`);

# screen input for bad characters

$last =~ s/[;`|&(),!$<>]//g;
$first =~ s/[;`|&(),!$<>]//g;
$msg =~ s/[;`|&(),!$<>]//g;

# change carriage return to cr/lf 
$msg =~ s/\r/\n/g;


# assemble guestbook entry

$gb_entry = "\"\<p\>\<b\>$first $last\</b\> \($msgid\) wrote:\n";
$gb_entry .= "\<pre\>\n$msg\n\</pre\>\</p\>\"";

# attach entry to the guestbook

$failed = system ("echo $gb_entry >> ./guestbook.txt");





### HTML page header

print "Content-type: text/html\n\n";
system ("cat ./templates/header.html");

### End header


if ($failed == 0) {

    print "<h2>Feedback received</h2>\n";
    print "<p>Your feedback has been received and will be soon screened for content</p>";
    print "<p>After we were the target of humiliating jokes for so long, we would really appreciate a friendly message.</p>";
    print "<p>You can view your comments in our <a href=\"/cgi-bin/guestbook.pl\">Guestbook</a>.</p>";

} else {
    print "<h2>Saving message failed</h2>\n";
}


### HTML page footer

system ("cat ./templates/footer.html");

### End footer

