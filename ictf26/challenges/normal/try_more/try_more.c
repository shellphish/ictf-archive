#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void win(void) {
    printf("Good job :D\n");
    static char *args[] = {"/bin/bash", "-i", NULL};
    execve("/bin/bash", args, NULL);
    _exit(0);
}

void vuln(void) {
    char buf[32];

    puts("Tell me your name and I'll say hello!");
    printf("> ");

    read(STDIN_FILENO, buf, 256);

    printf("Hello, %s!\n", buf);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin,  NULL, _IONBF, 0);

    puts("====================================");
    puts("   Slice of PIE  — CTF Challenge");
    puts("====================================");

    vuln();

    puts("Failure");
    return 0;
}
