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

ipaddr=$1
flag=$2;
password=$3;


# patch the source code and install the server program
if [ ! -e icecast-2.0-beta-1 ]; then
    echo "icecast-2.0-beta-1 not found in local directory";
    exit 1;
else
    cat ./sock.c | sed "s/##ICECAST_FLAG##/${flag}/" > icecast-2.0-beta-1/src/net/sock.c 
    cd icecast-2.0-beta-1
    make > /dev/null || exit 1
    make install > /dev/null || exit 1
    cd ..
    cat ./icecast.xml | sed "s/##ICECAST_PASSWD##/${password}/" > /usr/local/etc/icecast.xml
fi



# copy the init script to the correct location and make a link there
cp ./init_ices ${ScriptDir}
cp ./init_icecast ${ScriptDir}
rm -f ${InitDir}/S60ices
rm -f ${InitDir}/S61icecast
ln -s ${ScriptDir}/init_ices ${InitDir}/S60ices
ln -s ${ScriptDir}/init_icecast ${InitDir}/S61icecast


# patch icecast url
PAGE=/var/www/html/products/index.html
sed "s,@@IPADDR@@,$ipaddr,g" <$PAGE.in >$PAGE
 
