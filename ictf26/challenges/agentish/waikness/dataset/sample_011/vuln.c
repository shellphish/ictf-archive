#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: send_mail <recipient>");
        return 1;
    }
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "echo 'hello' | mail -s 'test' %s", argv[1]);
    system(cmd);
    return 0;
}
