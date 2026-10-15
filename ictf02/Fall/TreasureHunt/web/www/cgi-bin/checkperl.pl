#!/usr/bin/perl

print "Content-Type: text/html\n";

print "\n";

print "Checking file $ARGV[0] \n";

system("/usr/bin/perl -c $ARGV[0]");

print "Source: \n";

system("cat $ARGV[0]");

