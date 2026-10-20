#gcc -o $SERVICE_USER main.c screens.c util.c my_poi.c dbhelper.c registration.c help.c exit.c -fno-stack-protector
cp $SERVICE_USER $DESTDIR/usr/ctf/$SERVICE_USER
