#!/bin/bash -eu

mkdir -p $DESTDIR/opt/prison/bin
tar xvzf $PWD/prison.tar.gz -C $DESTDIR/opt/

gcc -o $DESTDIR/opt/prison/bin/toilet toilet.c -lcrypto
cp eat $DESTDIR/opt/prison/bin/
cp toilet.c.swo $DESTDIR/opt/prison/bin/.toilet.c.swo

cat <<END > $DESTDIR/opt/prison/startup.sh
#!/bin/sh
export HOME=/opt/prison
cd /opt/prison
exec script -q -c 'timeout -k 9 20 rbash -i' /dev/null
END
chmod 755 $DESTDIR/opt/prison/startup.sh

mkdir -p $DESTDIR/etc/xinetd.d/
cat <<END > $DESTDIR/etc/xinetd.d/prison
service prison
{
	disable		= no
	type		= unlisted
	flags		= reuse
	socket_type	= stream
	protocol	= tcp
	user		= nobody
	wait		= no
	port		= 911
	server		= /opt/prison/startup.sh
}
END
