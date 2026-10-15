#!/bin/bash


#
# SET THE APACHE ROOT TO THE CORRECT VALUE AND MAKE SURE THAT THERE IS NO TRAILING /
#
ApacheRoot=/var/www
ScriptDir=/root/scripts

if [ $# -lt 3 ]; then
    echo "usage: $0 ipaddr flag admin-pass";
    exit 1;
fi

# copy guestbook to correct location and set permissions accordingly
if [ ! -e guestbook.txt ]; then
    echo "guestbook not found in local directory";
    exit 1;
else
    cat guestbook.txt | sed "s/##GUESTBOOK_FLAG##/$2/" > ${ApacheRoot}/cgi-bin/guestbook.txt
    chown apache ${ApacheRoot}/cgi-bin/guestbook.txt
    chgrp root ${ApacheRoot}/cgi-bin/guestbook.txt
    chmod 600 ${ApacheRoot}/cgi-bin/guestbook.txt
fi
 

# copy guestbook administration scripts
if [ ! -e guestbook_admin.pl ]; then
    echo "guestbook_admin.pl not found in local directory";
    exit 1;
else
    admin=`perl -e "use Digest::MD5 qw(md5_hex); \\\$digest = md5_hex($3); print \\\$digest;"`;
    cat guestbook_admin.pl | sed "s/##GUESTBOOK_ADMIN_PASS##/${admin}/" >  ${ApacheRoot}/cgi-bin/guestbook_admin.pl
    chown root ${ApacheRoot}/cgi-bin/guestbook_admin.pl
    chgrp root ${ApacheRoot}/cgi-bin/guestbook_admin.pl
    chmod 755 ${ApacheRoot}/cgi-bin/guestbook_admin.pl
fi

if [ ! -e save_messages_admin.pl ]; then
    echo "save_messages_admin.pl not found in local directory";
    exit 1;
else
    admin=`perl -e "use Digest::MD5 qw(md5_hex); \\\$digest = md5_hex($3); print \\\$digest;"`;
    cat save_messages_admin.pl | sed "s/##GUESTBOOK_ADMIN_PASS##/${admin}/" >  ${ApacheRoot}/cgi-bin/save_messages_admin.pl
    chown root ${ApacheRoot}/cgi-bin/save_messages_admin.pl
    chgrp root ${ApacheRoot}/cgi-bin/save_messages_admin.pl
    chmod 755 ${ApacheRoot}/cgi-bin/save_messages_admin.pl
fi


# create init script
if [ ! -e init ]; then
    echo "init template not found in local directory";
    exit 1;
else
    ApacheRootEscaped=`echo ${ApacheRoot} | sed 's/\\//\\\\\//g'`
    cat init | sed "s/##GUESTBOOK_FLAG##/$2/" | sed "s/##APACHE_ROOT##/${ApacheRootEscaped}/" > init_guestbook
    chmod 700 init_guestbook
fi

# copy init_script to correct location
cp init_guestbook ${ScriptDir}
