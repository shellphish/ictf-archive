#!/usr/bin/perl

# use this script to change the password of accounts 
# to the hash of the username
# cat passwd.file | ./setpwd.pl > passwd.new

# get line from stdin
while (<>) {
    # parse line
    ($username, $passwd, $uid, $gid, $info, $home, $shell) = split(/:/);

    $salt = $passwd;
    $passwd = crypt($username, $salt);
 
    print "${username}:${passwd}:${uid}:${gid}:${info}:${home}:${shell}";
}





