#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: enable_debug <key>");
        return 1;
    }
    const char *DEBUG_KEY = "d3bug_3nabl3d";
    if (strcmp(argv[1], DEBUG_KEY) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("debug disabled");
    return 2;
}
