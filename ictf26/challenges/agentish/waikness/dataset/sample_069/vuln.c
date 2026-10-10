#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: verify <key>");
        return 1;
    }
    const char *API_KEY = "xK9mP2vL8nQ4rT6w";
    if (strcmp(argv[1], API_KEY) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("invalid key");
    return 2;
}
