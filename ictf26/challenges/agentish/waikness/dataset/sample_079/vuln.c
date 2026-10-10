#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: verify_cert <cert>");
        return 1;
    }
    char master_key[] = "M4st3rK3y2024";
    if (memcmp(argv[1], master_key, strlen(master_key)) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("cert invalid");
    return 2;
}
