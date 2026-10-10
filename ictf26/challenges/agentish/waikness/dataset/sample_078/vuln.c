#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: authenticate <credential>");
        return 1;
    }
    char cred[] = "C0nf1dent!al";
    if (strcmp(argv[1], cred) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("failed");
    return 2;
}
