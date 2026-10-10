#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: traceroute_host <host>");
        return 1;
    }
    char buf[256];
    snprintf(buf, sizeof(buf), "traceroute %s", argv[1]);
    system(buf);
    return 0;
}
