.PHONY: all clean

all: token_of_appreciation

clean:
	rm -f token_of_appreciation *.yy.c

%.yy.c: %.l
	echo "flex -o $@ $<"
	flex -o $@ $<

.PRECIOUS: %.yy.c

%: %.yy.c
	echo "gcc -O2 -o $@ $< -lfl"
	gcc -O2 -o $@ $< -lfl