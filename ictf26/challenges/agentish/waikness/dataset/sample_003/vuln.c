#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: file_info <path>");
        return 1;
    }
    char command[512];
    snprintf(command, sizeof(command), "file %s", argv[1]);
    system(command);
    return 0;
}
