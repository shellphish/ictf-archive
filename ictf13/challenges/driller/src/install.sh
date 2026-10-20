g++ -S main.cpp GlobalState.cpp Helper.cpp User.cpp Spot.cpp Driller.cpp Menu.cpp -m32 -Wno-write-strings -O3
g++ main.s GlobalState.s Helper.s User.s Spot.s Driller.s Menu.s -m32 -Llibs -lcryptopp -lsqlite3 -Wno-write-strings -o ude
strip ude
rm *.s
mv ude $DESTDIR/usr/ctf/$SERVICE_USER
