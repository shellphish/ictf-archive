#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: lookup <host>");
        return 1;
    }
    char buf[256];
    snprintf(buf, sizeof(buf), "nslookup %s", argv[1]);
    system(buf);
    return 0;
}
