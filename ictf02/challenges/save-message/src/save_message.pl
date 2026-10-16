#!/usr/bin/perl

use CGI qw/:standard/;
#use strict;

print header('text/html');

my $last = param('last');
my $first = param('first');
my $msg = param('comment');
my $filename =  join "",${last},${first};

print start_html("Feedback received!");

print h1("Feedback received!");

print "<p>Your feedback has been received and will be soon screened for content</p>";

print "<p>If you wrote anything bad about us, your comments will be destroyed (and we will probably break your legs, too)</p>";

print "<p>If your comments were extremely positive they will be published in our <a href=\"/cgi-bin/guestbook.pl?guestbook.txt\">Guestbook</a>.</p>";


# print "last $last first $first file $filename msg (${msg})";

open MSGFILE, "> $filename" or print "Can't open file $filename";

print MSGFILE $msg, ;

print end_html;
