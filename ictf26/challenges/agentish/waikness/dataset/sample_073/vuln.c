#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: gate <code>");
        return 1;
    }
    const char *CODE = "A3F7B2D9";
    if (strcmp(argv[1], CODE) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("denied");
    return 2;
}
