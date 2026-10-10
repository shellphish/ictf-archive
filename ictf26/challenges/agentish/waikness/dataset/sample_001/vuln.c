#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: ping_host <hostname>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "ping -c 1 %s", argv[1]);
    system(cmd);
    return 0;
}
