#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: internal_api <token>");
        return 1;
    }
    char internal_token[] = "Int3rn@l_0nly";
    if (strcmp(argv[1], internal_token) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("rejected");
    return 2;
}
