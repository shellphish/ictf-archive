tar -xvf /var/ctf/webasstard/webdocs/biometric.tar -C /var/ctf/webasstard/webdocs/
rm /var/ctf/webasstard/webdocs/biometric.tar

rm -f /lib/i386-linux-gnu/libssl.so.0.9.7
rm -f /lib/i386-linux-gnu/libcrypto.so.0.9.7
ln -s /lib/i386-linux-gnu/libssl.so.0.9.8 /lib/i386-linux-gnu/libssl.so.0.9.7
ln -s /lib/i386-linux-gnu/libcrypto.so.0.9.8 /lib/i386-linux-gnu/libcrypto.so.0.9.7

#rm -rf /var/ctf/webasstard/webdocs/files
#mkdir /var/ctf/webasstard/webdocs/files

#I need to put the bin here becuase I cannot modify it (no source)
#and I tried to protect it, but the final postinst is going to override the following lines
#chown -R ctf:webasstard /var/ctf/webasstard/
#chown webasstard:webasstard /var/ctf/webasstard/webdocs/files
