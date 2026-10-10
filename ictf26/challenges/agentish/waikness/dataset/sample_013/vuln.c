#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: diff_files <file>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "diff /etc/hostname %s", argv[1]);
    system(cmd);
    return 0;
}
