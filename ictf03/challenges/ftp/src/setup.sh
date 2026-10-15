#!/bin/bash

#
# SET THE INSTALL DIRS TO THE CORRECT VALUES AND MAKE SURE THAT THERE IS NO TRAILING /
#
InstallDir=/usr/local/sbin
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
if [ ! -e weirdftp.c ]; then
    echo "weirdftp.c not found in local directory";
    exit 1;
else
    cat weirdftp.c | sed "s/##FTP_FLAG##/$2/" | sed "s/##FTP_PASS##/${password}/" > ftpd.c
    gcc -DLINUX -o ftpd ftpd.c -lcrypt 2> /dev/null
    if [ $? -ne 0 ]; then
	echo "compilation of ftpd.c failed. do you have libcrypt?";
	exit 1;
    fi
    cp ftpd ${InstallDir}
fi

# setup the correct permissions
chown root:root ${InstallDir}/ftpd
chmod 700 ${InstallDir}/ftpd 


# copy the init script to the correct location and make a link there
cp ./init_ftp ${ScriptDir}
rm -f ${InitDir}/S92ftp
ln -s ${ScriptDir}/init_ftp ${InitDir}/S92ftp

