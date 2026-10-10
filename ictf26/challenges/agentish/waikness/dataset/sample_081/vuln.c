#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: recovery <phrase>");
        return 1;
    }
    char recovery_phrase[] = "yellow-moon-river";
    if (strcmp(argv[1], recovery_phrase) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("invalid phrase");
    return 2;
}
