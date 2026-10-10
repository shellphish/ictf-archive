AM_CFLAGS = -g -Wall
#AM_CFLAGS = -Wall -static -DDEBUG

noinst_HEADERS = netheaders.h mydiag.h

bin_PROGRAMS = weirdtcp attack

weirdtcp_SOURCES = weirdtcp.c mydiag.c mydiag.h netheaders.h
attack_SOURCES = attack.c netheaders.h

dist-hook:
	rm -f  $(distdir)/*~
