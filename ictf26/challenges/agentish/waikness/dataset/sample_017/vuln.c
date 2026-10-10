#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: net_connect <host:port>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "nc -zv %s", argv[1]);
    system(cmd);
    return 0;
}
