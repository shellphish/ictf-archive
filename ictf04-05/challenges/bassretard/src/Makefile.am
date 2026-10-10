AM_CFLAGS = -Wall -g -DDEBUG

bin_PROGRAMS = bassretard
pkgdata_DATA = basstard.css

EXTRA_DIST = bassretard.sh basstard.css

bassretard_SOURCES = bassretard.c



install-data-hook:
	$(INSTALL_DATA) -m 755 bassretard.sh /etc/init.d/bassretard
	/usr/sbin/useradd -d /  bassretard

uninstall-hook:
	$(RM) /etc/init.d/bassretard 
	/usr/sbin/userdel bassretard

dist-hook:
	rm -f  $(distdir)/*~

