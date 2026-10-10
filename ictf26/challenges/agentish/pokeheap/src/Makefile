CC     = gcc
CFLAGS = -O0 -no-pie -fno-stack-protector -z execstack -D_FORTIFY_SOURCE=0
TARGETS = level1

all: $(TARGETS)

level1: level1.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGETS)

.PHONY: all clean
