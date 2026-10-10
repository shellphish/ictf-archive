#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: read_share <filename>");
        return 1;
    }
    char path[512];
    snprintf(path, sizeof(path), "/mnt/share/%s", argv[1]);
    FILE *f = fopen(path, "r");
    if (!f) {
        puts("file not found");
        return 1;
    }
    char buf[512];
    while (fgets(buf, sizeof(buf), f)) fputs(buf, stdout);
    fclose(f);
    return 0;
}
