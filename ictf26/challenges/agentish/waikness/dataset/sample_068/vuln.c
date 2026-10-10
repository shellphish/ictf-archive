#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: login <token>");
        return 1;
    }
    const char *TOKEN = "s3cr3t_t0k3n";
    if (strcmp(argv[1], TOKEN) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("invalid token");
    return 2;
}
