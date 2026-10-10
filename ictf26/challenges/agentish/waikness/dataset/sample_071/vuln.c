#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: access <passphrase>");
        return 1;
    }
    char passphrase[] = "open_sesame";
    if (strcmp(argv[1], passphrase) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("access denied");
    return 2;
}
