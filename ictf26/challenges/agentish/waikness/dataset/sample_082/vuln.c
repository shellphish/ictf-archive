#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: service_auth <key>");
        return 1;
    }
    const char *SVC_KEY = "svc-xT8kP3mL9nW";
    if (strcmp(argv[1], SVC_KEY) == 0) {
        system("cat /flag");
        return 0;
    }
    puts("unauthorized");
    return 2;
}
