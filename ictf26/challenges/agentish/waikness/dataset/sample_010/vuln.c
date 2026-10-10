#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: show_process <name>");
        return 1;
    }
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "ps aux | grep %s", argv[1]);
    system(cmd);
    return 0;
}
