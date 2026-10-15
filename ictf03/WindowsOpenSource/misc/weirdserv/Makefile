all: encode weirdftpd weirdfind weirdfindc
CFLAGS = -g -Wall -DDEBUG -DLINUX
#CFLAGS = -Wall -DLINUX
#CFLAGS = -g -Wall -DDEBUG
LDFLAGS = -lcrypt
#LDFLAGS = 

encode: encode.c
	gcc ${CFLAGS} encode.c -o encode ${LDFLAGS}

weirdftpd: weirdftpd.c
	gcc ${CFLAGS} weirdftpd.c -o weirdftpd ${LDFLAGS}

weirdfind: weirdfind.c
	gcc ${CFLAGS} weirdfind.c -o weirdfind ${LDFLAGS}

weirdfindc: weirdfindc.c
	gcc ${CFLAGS} weirdfindc.c -o weirdfindc

clean:
	rm encode weirdftpd weirdfind weirdfindc


