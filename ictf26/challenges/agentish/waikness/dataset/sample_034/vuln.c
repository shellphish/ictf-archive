#include <stdio.h>
#include <string.h>

#define BASE_DIR "/var/www/files/"

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: read_file <filename>");
        return 1;
    }
    char path[512];
    snprintf(path, sizeof(path), "%s%s", BASE_DIR, argv[1]);
    FILE *f = fopen(path, "r");
    if (!f) {
        puts("file not found");
        return 1;
    }
    char buf[1024];
    while (fgets(buf, sizeof(buf), f))
        fputs(buf, stdout);
    fclose(f);
    return 0;
}
