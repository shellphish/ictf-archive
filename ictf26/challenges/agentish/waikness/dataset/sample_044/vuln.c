#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: load_module <module>");
        return 1;
    }
    char path[512];
    snprintf(path, sizeof(path), "/usr/lib/modules/%s", argv[1]);
    FILE *f = fopen(path, "r");
    if (!f) {
        puts("module not found");
        return 1;
    }
    char buf[512];
    while (fgets(buf, sizeof(buf), f)) fputs(buf, stdout);
    fclose(f);
    return 0;
}
