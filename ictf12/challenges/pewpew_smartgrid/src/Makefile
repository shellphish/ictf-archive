CC = gcc
CFLAGS = -m32 -Wpointer-to-int-cast -static -Wno-format-security -U_FORTIFY_SOURCE

all: normal

normal:
	${CC} -O3 ${CFLAGS} -o pewpew pewpew.c 
	execstack -s pewpew
	strip pewpew

debug:
	${CC} -O0 ${CFLAGS} -g -DDEBUG -o pewpew pewpew.c 

clean:
	rm pewpew
