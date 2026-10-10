#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: check_pass <password>");
        return 1;
    }
    char stored[] = "p@ssw0rd123";
    if (strcmp(argv[1], stored) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("wrong password");
    return 2;
}
