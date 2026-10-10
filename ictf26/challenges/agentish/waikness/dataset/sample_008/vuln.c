#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: log_search <pattern>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "grep -r '%s' /var/log/", argv[1]);
    system(cmd);
    return 0;
}
