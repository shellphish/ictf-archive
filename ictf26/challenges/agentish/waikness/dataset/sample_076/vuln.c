#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: validate <hash>");
        return 1;
    }
    char hardcoded_hash[] = "deadbeefcafe1337";
    if (strncmp(argv[1], hardcoded_hash, 16) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("invalid");
    return 2;
}
