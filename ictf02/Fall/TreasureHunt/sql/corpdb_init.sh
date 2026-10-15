#!/bin/sh

# Initializes the CorpDB
#
# Remember to add user dbuser with password supersecret to your
# MySQL config file
#
# Command-line options:
#
#   -u   database username          (DEF: 'dbuser')
#   -p   database password          (DEF: 'supersecret')
#   -db  database name              (DEF: 'corpdb')
#   -h   db-server hostname         (DEF: 'localhost')
#   -s   sql-script to source       (DEF: 'corpdb_init.sql}')

# where are we?
MYFILE="$0"
while [ -L "$MYFILE" ] ; do
    target=`expr "\`ls -l $MYFILE\`" : '.*-> \(.*\)$'`
    if echo "$target" | grep '^/' > /dev/null; then
        MYFILE="$target"                     # absolute path
    else
        MYFILE=`dirname $MYFILE`/$target     # relative path
    fi
done
SCRIPTLOC=`dirname $MYFILE`/corpdb_init.sql

USERNAME=""
PASSWORD=""
DATABASE_NAME=""
SERVER_HOSTNAME=""
SQL_SCRIPT_PATH=""
CURRENT=""

for arg 
do

TEMP=$arg

if [ "${CURRENT}" = "USERNAME" ]
then
    USERNAME=$arg; CURRENT=""
fi

if [ "${CURRENT}" = "PASSWORD" ]
then
    PASSWORD=$arg; CURRENT=""
fi

if [ "${CURRENT}" = "DATABASE_NAME" ]
then
    DATABASE_NAME=$arg; CURRENT=""
fi

if [ "${CURRENT}" = "SERVER_HOSTNAME" ]
then
    SERVER_HOSTNAME=$arg; CURRENT=""
fi

if [ "${CURRENT}" = "SQL_SCRIPT_PATH" ]
then
    SQL_SCRIPT_PATH=$arg; CURRENT=""
fi


if [ "${TEMP}" = "-u" ]
then
	CURRENT="USERNAME";
fi

if [ "${TEMP}" = "-p" ]
then
	CURRENT="PASSWORD";
fi

if [ "${TEMP}" = "-db" ]
then
	CURRENT="DATABASE_NAME";
fi

if [ "${TEMP}" = "-h" ]
then
	CURRENT="SERVER_HOSTNAME";
fi

if [ "${TEMP}" = "-s" ]
then
	CURRENT="SQL_SCRIPT_PATH";
fi


done

echo '#INITIALIZING CORP DATABASE' 

if [ "$USERNAME" = "" ]; then
    USERNAME="dbuser"; 
    echo "# username        = ${USERNAME} (default)";
else
    echo "# username        = ${USERNAME}"
fi

if [ "$PASSWORD" = "" ]; then
    PASSWORD="supersecret"; 
    echo "# password        = ${PASSWORD} (default)";
else
    echo "# password        = ${PASSWORD}"
fi

if [ "$DATABASE_NAME" = "" ]; then
    DATABASE_NAME="corpdb"; 
    echo "# database        = ${DATABASE_NAME} (default)";
else
    echo "# database        = ${DATABASE_NAME}"
fi

if [ "$SERVER_HOSTNAME" = "" ]; then
    SERVER_HOSTNAME="localhost"; 
    echo "# server hostname = ${SERVER_HOSTNAME} (default)";
else
    echo "# server hostname = ${SERVER_HOSTNAME}"
fi

if [ "$SQL_SCRIPT_PATH" = "" ]; then
    SQL_SCRIPT_PATH=$SCRIPTLOC; 
    echo "# sql script = ${SQL_SCRIPT_PATH} (default)";
else
    echo "# sql script = ${SQL_SCRIPT_PATH}"
fi


echo '# Executing  '
echo "mysql -t -h ${SERVER_HOSTNAME} -u ${USERNAME} -p${PASSWORD} ${DATABASE_NAME} < ${SQL_SCRIPT_PATH}"

# mysql -t -h ${SERVER_HOSTNAME} -u ${USERNAME} -p${PASSWORD} ${DATABASE_NAME} < ${SQL_SCRIPT_PATH}










