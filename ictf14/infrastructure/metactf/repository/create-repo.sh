#!/bin/bash

set -eux

(( $# >= 2 ))

SECRET_KEY_FILE="$1"
shift
BASE="$2"
shift
# packages: "$@"

gpg --import ${SECRET_KEY_FILE}

# These should not be public
mkdir -p "$BASE/db" "$BASE/conf"
chmod -R go-rwx "$BASE/db" "$BASE/conf"

echo """
Origin: iCTF
Label: iCTF
Suite: trusty
Codename: trusty
Version: 3.0
Architectures: amd64
Components: main
Description: Service packages for the iCTF - Hacking at Scale
SignWith: yes
""" > "$BASE/conf/distributions"

reprepro -b "$BASE" installdeb

for deb in "$@"; do
    dpkg-sig -m iCTF --sign builder "$deb"
    reprepro --ask-passphrase -V -b "$BASE" includedeb trusty "$deb"
done

reprepro -b "$BASE" createsymlinks
reprepro -b "$BASE" check


echo
echo "Good! Now expose $BASE/pool and $BASE/dists to the world! (symlinks in /var/www/ictf, for instance)"
