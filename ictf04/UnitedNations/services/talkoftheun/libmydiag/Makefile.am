AM_CFLAGS       = -g -Wall 
include_HEADERS	= mydiag.h

lib_LIBRARIES = libmydiag.a
libmydiag_a_SOURCES = mydiag.c mydiag.h

dist-hook:
	rm -f  $(distdir)/*~
