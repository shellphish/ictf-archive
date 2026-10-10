#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: backdoor <magic>");
        return 1;
    }
    const char magic[] = "hunter2";
    if (strcmp(argv[1], magic) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("no");
    return 2;
}
