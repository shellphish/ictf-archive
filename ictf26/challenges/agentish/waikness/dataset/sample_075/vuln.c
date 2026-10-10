#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: admin <secret>");
        return 1;
    }
    const char *ADMIN_SECRET = "fl4g_1s_h3r3";
    if (strcmp(argv[1], ADMIN_SECRET) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("not admin");
    return 2;
}
