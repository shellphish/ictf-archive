#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: read_log <logname>");
        return 1;
    }
    char path[512];
    snprintf(path, sizeof(path), "/var/log/%s", argv[1]);
    FILE *f = fopen(path, "r");
    if (!f) {
        puts("log not found");
        return 1;
    }
    char line[256];
    while (fgets(line, sizeof(line), f)) fputs(line, stdout);
    fclose(f);
    return 0;
}
