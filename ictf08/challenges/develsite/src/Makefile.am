AM_CFLAGS = -Wall
bin_PROGRAMS	= softerror
softerror_SOURCES = softerror.c util.asm mydiag.h

.asm.o:
	nasm -f elf32 -o $@ $<

dist-hook:
	rm -f  $(distdir)/*~
