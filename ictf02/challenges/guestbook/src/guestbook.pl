#!/usr/bin/perl
use CGI qw/:standard/;

print header('text/html');

print start_html("The Bass Tard Corporation Guestbook");

my $guestfile = $ENV{QUERY_STRING};

system("echo \"Welcome! This is our guestbook\"; cat $guestfile");

print end_html;
