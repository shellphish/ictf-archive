AM_CFLAGS = -g -Wall 
bin_PROGRAMS	= webasstard
webasstard_SOURCES = webasstard.c
EXTRA_DIST = webasstard.pem webasstard-ca_signed.pem webasstard-self_signed.crt index.html webasstard.conf create_docs.sh basstard.css biometric biometric-linux biometric-macos



dist-hook:
	rm -f  $(distdir)/*~
