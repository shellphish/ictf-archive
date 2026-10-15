#!/bin/sh

#
# SET THE APACHE ROOT TO THE CORRECT VALUE AND MAKE SURE THAT THERE IS NO TRAILING /
#
ApacheRoot=/var/www
ScriptDir=/root/scripts

if [ $# -lt 4 ]; then
    echo "usage: $0 ipaddr flag admin-pass db-pass";
    exit 1;
fi


# copy query scripts
if [ ! -e query_extension.pl ]; then
    echo "query_extension.pl not found in local directory";
    exit 1;
else
    cat query_extension.pl | sed "s/##QUERY_DB_PASS##/$4/" >  ${ApacheRoot}/cgi-bin/query_extension.pl
    chown root ${ApacheRoot}/cgi-bin/query_extension.pl
    chgrp root ${ApacheRoot}/cgi-bin/query_extension.pl
    chmod 755 ${ApacheRoot}/cgi-bin/query_extension.pl
fi

if [ ! -e change.pl ]; then
    echo "change.pl not found in local directory";
    exit 1;
else
    admin=`perl -e "use Digest::MD5 qw(md5_hex); \\\$digest = md5_hex($3); print \\\$digest;"`;
    cat change.pl | sed "s/##QUERY_ADMIN_PASS##/${admin}/" | sed "s/##QUERY_DB_PASS##/$4/" >  ${ApacheRoot}/cgi-bin/change.pl
    chown root ${ApacheRoot}/cgi-bin/change.pl
    chgrp root ${ApacheRoot}/cgi-bin/change.pl
    chmod 755 ${ApacheRoot}/cgi-bin/change.pl
fi


# setup the database user
dropdb querydb;
createdb querydb;
psql -e -d querydb -c "DROP USER \"queryuser\"";
psql -e -d querydb -c "CREATE USER \"queryuser\" WITH  PASSWORD '$4' NOCREATEDB NOCREATEUSER";



# create init script
if [ ! -e init ]; then
    echo "init template not found in local directory";
    exit 1;
else
    cat init | sed "s/##QUERY_FLAG##/$2/" > init_query
    chmod 700 init_query
fi

# execute it to initialize database
./init_query


# copy it to correct location
cp ./init_query ${ScriptDir}
