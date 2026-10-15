#!/bin/bash

#
# SET THE INSTALL DIRS TO THE CORRECT VALUES AND MAKE SURE THAT THERE IS NO TRAILING /
#
InstallDir=/var/sfind
InitDir=/etc/rc3.d
ScriptDir=/root/scripts

# check for arguments
if [ $# -lt 3 ]; then
    echo "usage: $0 ipaddr flag pass";
    exit 1;
fi


if [ ! -e encode ]; then
    echo "encode not found in local directory";
    exit 1;
fi

pass=`./encode -p $3`
echo $pass | sed 's/\([&/\]\)/\\\1/g' > pw.file
password=`cat pw.file`
rm pw.file
 
# patch the source code and install the server program
if [ ! -e weirdfind.c ]; then
    echo "weirdfind.c not found in local directory";
    exit 1;
else
    cat weirdfind.c | sed "s/##FIND_FLAG##/$2/" | sed "s/##FIND_PASS##/${password}/" > sfind.c
    gcc -o sfind sfind.c -lcrypt 2> /dev/null
    if [ $? -ne 0 ]; then
	echo "compilation of sfind.c failed. do you have libcrypt?";
	exit 1;
    fi
    cp sfind  ${InstallDir}/sfind
fi


# setup the correct permissions
chown sfind ${InstallDir}/sfind
chgrp sfind ${InstallDir}/sfind
chmod 755   ${InstallDir}/sfind 



# copy the init script to the correct location and make a link there
cp ./init_sfind ${ScriptDir}
rm -f ${InitDir}/S91sfind
ln -s ${ScriptDir}/init_sfind ${InitDir}/S91sfind



 
