#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: archive <dir>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "tar -czf output.tar.gz %s", argv[1]);
    system(cmd);
    return 0;
}
