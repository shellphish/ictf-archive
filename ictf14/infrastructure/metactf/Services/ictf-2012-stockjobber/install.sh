cobc -x -o $SERVICE_USER StockJobber.cbl AddUser.cbl AuthenticateUsers.cbl Authorizer.cbl CheckBank.cbl ListUsers.cbl MaidenManager.cbl RSA.cbl
mv $SERVICE_USER $DESTDIR/usr/ctf/$SERVICE_USER

cat <<END > $DESTDIR/usr/ctf/$SERVICE_USER/startup.sh
#!/bin/sh
cd /usr/ctf/$SERVICE_USER
exec ./$SERVICE_USER
END
chmod 755 $DESTDIR/usr/ctf/$SERVICE_USER/startup.sh

mkdir -p $DESTDIR/etc/xinetd.d/
cat <<END > $DESTDIR/etc/xinetd.d/stockjobber
service stockjobber
{
	disable		= no
	type		= unlisted
	flags		= reuse
	socket_type	= stream
	protocol	= tcp
	user		= $SERVICE_USER
	wait		= no
	port		= 2583
	server		= /usr/ctf/$SERVICE_USER/startup.sh
}
END
