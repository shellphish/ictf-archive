javac -cp android.jar DexWare.java FileDescriptorCleaner.java
./dx --dex --output=dexware.jar *.class
rm *.class
gcc -I/usr/lib/jvm/java-7-openjdk-amd64/include -shared -o FileDescriptorCleaner.so -m32 -fPIC FileDescriptorCleaner.c 
cp -r linux-x86 $DESTDIR/usr/ctf/$SERVICE_USER
mv $SERVICE_USER.jar FileDescriptorCleaner.so $DESTDIR/usr/ctf/$SERVICE_USER
install dalvik run.sh $DESTDIR/usr/ctf/$SERVICE_USER
