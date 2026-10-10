#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: compress <file>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "gzip -k %s", argv[1]);
    system(cmd);
    return 0;
}
