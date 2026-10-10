#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: word_count <filename>");
        return 1;
    }
    char cmd[512];
    sprintf(cmd, "wc -l %s", argv[1]);
    system(cmd);
    return 0;
}
