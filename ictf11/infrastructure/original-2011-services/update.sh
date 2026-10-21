#!/bin/bash

DRYRUN=""
# CREATE USER 'mulemanager'@'localhost' IDENTIFIED BY 'grabthiswhileyoucan';
SERVER="muleserver"
DBUSER="mulemanager"
DBPASSWORD="grabthiswhileyoucan"
REDODB="no"
while getopts "ds:nb" opt; do
    case $opt in
        d)
            DEBUG=1
            ;;
        s) 
            SERVER="$OPTARG"
            ;;
	n)
	    DRYRUN="-n"
	    ;;
	b)
	    REDODB="yes"
	    ;;
        ?) 
            echo "Invalid option."
            exit 1
            ;;
    esac
done

if [ -z $SERVER ]; then
	echo "Missing server name" 
	exit 1
fi

if [ "$REDODB" == "yes" ]; then 
# Resets the database
    mysql5 --host $SERVER --user=$DBUSER --password=$DBPASSWORD mulemanager < mulemanager/sql/schema_init.sql
    mysql5 --host $SERVER --user=$DBUSER --password=$DBPASSWORD mulemanager < mulemanager/sql/db_populate.sql
fi

rsync -pravzl $DRYRUN --delete mulemanager/www/ root@$SERVER:/var/www/
rsync -pravzl $DRYRUN --delete muleregister/public_html/ muleregister@$SERVER:public_html/
rsync -pravzl $DRYRUN --delete muleadmin/public_html/ muleadmin@$SERVER:public_html/
rsync -pravzl $DRYRUN --delete muleuser/public_html/ muleuser@$SERVER:public_html/
rsync -pravzl $DRYRUN --delete msgdispatcher/code/ msgdispatcher@$SERVER:code/
exit 0
