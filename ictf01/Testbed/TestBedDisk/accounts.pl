#!/usr/bin/perl

# use this script to create home dirs from a passwd-like file
# cat passwd.file | ./accounts.pl | /bin/sh

# get line from stdin
while (<>) {
    # parse line
    ($username, $passwd, $uid, $gid, $info, $home, $shell) = split(/:/);

    print "mkdir ${home}\n";
    print "chown ${uid}:${gid} ${home}\n";
}





