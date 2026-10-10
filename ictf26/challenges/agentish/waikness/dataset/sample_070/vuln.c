#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: unlock <pin>");
        return 1;
    }
    char pin[] = "1337h4x0r";
    if (strncmp(argv[1], pin, strlen(pin)) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("wrong pin");
    return 2;
}
