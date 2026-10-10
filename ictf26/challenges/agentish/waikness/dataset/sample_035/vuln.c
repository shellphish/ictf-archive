#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: cat_doc <document>");
        return 1;
    }
    char path[512];
    snprintf(path, sizeof(path), "/home/user/documents/%s", argv[1]);
    FILE *fp = fopen(path, "r");
    if (!fp) {
        puts("cannot open file");
        return 1;
    }
    int c;
    while ((c = fgetc(fp)) != EOF) putchar(c);
    fclose(fp);
    return 0;
}
