#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char username[] = "alice";

void show_flag() {
    printf("\nADMIN ACCESS GRANTED!\n");
    static char *args[] = {"/bin/sh", "-i", NULL};
    execve("/bin/sh", args, NULL);
}

void vulnerable_function(char *user_input) {
    struct __attribute__((packed)) login_state {
        char buffer[64];
        int is_admin;
        int do_not_exagerate;
    } state = {0};
    
    printf("Welcome %s!\n", username);
    printf("Attempting login...\n");
    strcpy(state.buffer, user_input);
    printf("Buffer content: %s\n", state.buffer);
    
    if (state.is_admin && !state.do_not_exagerate) {
        show_flag();
    } else {
        printf("Login failed. You are not an admin.\n");
    }
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <input>\n", argv[0]);
        printf("\nChallenge: BOF_64_4443\n");
        printf("Goal: Overflow the buffer to set is_admin = 1\n");

        return 1;
    }
    vulnerable_function(argv[1]);
    return 0;
}
