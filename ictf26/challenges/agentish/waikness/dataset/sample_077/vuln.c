#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: sudo_check <password>");
        return 1;
    }
    const char *ROOT_PASS = "r00tp4ss!";
    if (strcmp(argv[1], ROOT_PASS) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("denied");
    return 2;
}
