#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: checksum <file>");
        return 1;
    }
    char buf[512];
    snprintf(buf, sizeof(buf), "md5sum %s", argv[1]);
    system(buf);
    return 0;
}
