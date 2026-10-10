#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: strings_tool <file>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "strings %s", argv[1]);
    system(cmd);
    return 0;
}
