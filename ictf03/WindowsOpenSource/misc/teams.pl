#!/usr/bin/perl
${imagedir} = "Public/CTF/images/";
#${imagedir} = "Test/images/";
${authfileremote} = "/cs/rsl/vigna/.htpasswd";
${authfilelocal} = "htpasswd";

# get line from stdin
while (<>) {
    # parse line
    (${dir}, ${pass}) = split(/:/);

    open F, "> ${imagedir}/${dir}/.htaccess" or die "Can't open ${imagedir}/${dir}/.htaccess: $!";
    
    print F "AuthUserFile ${authfileremote}\n\
AuthGroupFile /dev/null\n\
AuthName ${dir}\n\
AuthType Basic\n\
require user ${dir}\n";
    
    system("htpasswd -b ${authfilelocal} ${dir} ${pass}");
}
