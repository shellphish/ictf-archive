gcc -o $DESTDIR/usr/ctf/$SERVICE_USER/$SERVICE_USER $SERVICE_USER.c mydiag.c zocket.c -lssl -lcrypto
install talkserver.pem talkserver.key talkserver.txt $DESTDIR/usr/ctf/$SERVICE_USER/
touch $DESTDIR/var/ctf/$SERVICE_USER/passwd.txt
