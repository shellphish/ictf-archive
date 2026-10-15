#!/usr/bin/perl

# use this script to create home dirs from a passwd-like file
# cat passwd.file | ./accountsNT.pl | /bin/sh

# get line from stdin
while (<>) {
    # parse line
    ($username, $passwd, $uid, $gid, $info, $home, $shell) = split(/:/);

    print "mkdir /home/${username}\n";
    print "net user ${username} ${username} /add /homedir:C:/home/${username} /fullname:\"${info}\"\n";
}

# creates the password/group file used by ssh
print "mkpasswd -l > /etc/passwd\n";
print "mkgroup -l > /etc/group\n";




