#!/bin/bash

BUNDLE=$1
DEPS="lxml pexpect pycrypto Twisted rsa ecdsa BeautifulSoup networkx mechanize requests html5lib"
[ -z "$BUNDLE" ] && echo "Usage: $0 /path/to/team_ictf2014_XX.tar.gz" && exit
[ -z "$VIRTUAL_ENV" ] && echo "Please create (and workon) a virtualenv with all the script dependencies: $DEPS" && exit

echo "Unpacking..."
TMPDIR=/dev/shm/ctf-$RANDOM
mkdir -p $TMPDIR
cd $TMPDIR
tar xvzf $BUNDLE
TEAM_ID=$(ls -d *)
echo $TEAM_ID
cd - > /dev/null
cd $TMPDIR/$TEAM_ID

VM=$(ls vuln_*.ova)
VM=${VM%.ova}

echo "Importing..."
vboxmanage import $VM.ova
cd - > /dev/null
rm -rf $TMPDIR

echo "Reconfiguring..."
vboxmanage hostonlyif ipconfig vboxnet0 --ip 10.7.$TEAM_ID.1
vboxmanage modifyvm $VM --nic2 hostonly
vboxmanage modifyvm $VM --hostonlyadapter2 vboxnet0

echo "Starting..."
vboxmanage startvm $VM --type headless

echo "Sleeping for a minute to let everything boot"
sleep 60

echo "Testing..."
working=$(grep is_working Services/*/info.json | grep ': 1' | sed -e "s/:.*//")
for w in $working
do
	cd $(dirname $w)
	if ! ../../tester.py --once --info info.json --ip 10.7.$TEAM_ID.2 --no-exploit --virtualenv $VIRTUAL_ENV > ~/code/ictf/metactf/out/$(basename $w)
	then
		echo "FAIL: $w"
	else
		echo "PASS: $w"
	fi
	cd - >/dev/null
done

echo "Shutting down..."
vboxmanage controlvm $VM poweroff

echo "Deleting..."
vboxmanage unregistervm $VM --delete
