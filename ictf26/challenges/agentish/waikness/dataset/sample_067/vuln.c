#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: auth <password>");
        return 1;
    }
    const char *SECRET = "SUPERSECRET";
    if (strcmp(argv[1], SECRET) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("denied");
    return 2;
}
