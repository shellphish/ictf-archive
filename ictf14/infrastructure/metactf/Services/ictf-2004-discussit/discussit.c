#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <pwd.h>
#define DEFAULT_PORT 7413
#define BUFSIZE 512

void reaper(int sig) {
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0);
}

void doit() {
    char buffer[BUFSIZE];
    char operator[BUFSIZE];
    char topic[BUFSIZE];
    int i, numc;

    i = 0;
    while((numc = read(0, &(buffer[i]), 1)) == 1) {
        if (buffer[i] == '\n') {
            if (buffer[i - 1] == '\r') {
                buffer[i - 1] = '\0';
            } else {
                buffer[i] = '\0';
            }
            break;
        }
        i++;
    }

    sscanf(buffer, "%s %s", operator, topic);
    fprintf(stderr, "summoning operator %s on topic %s\n", operator, topic);
    i = execl("/usr/ctf/discussit/discussit-chat",
              "/usr/ctf/discussit/discussit-chat",
              operator, topic, (char *) NULL);
    perror("execl");
    fprintf(stderr, "operator not available %d \n",i);
    /* never reached */
    return;
}

int main(int argc, char *argv[]) {
    struct sockaddr_in server_addr;
    struct sockaddr client_addr;
    int sockfd, newsockfd, client_len;
    int port;
    int pid;
    int on = 1;

    if (argv[1] != NULL) {
        port = atoi(argv[1]);
    } else {
        port = DEFAULT_PORT;
    }

    bzero((char *) &server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    sockfd = socket(PF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        perror("socket");
        exit(1);
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR,
                   (char *)&on, sizeof(on)) == -1) {
        perror("setsockopt");
        return -1;
    }

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr))) {
        perror("bind");
        exit(1);
    }

    if (listen(sockfd, 5)) {
        perror("listen");
        exit(1);
    }

    (void) signal(SIGCHLD, reaper);

    while (1) {
        client_len = sizeof(client_addr);
        newsockfd = accept(sockfd, &client_addr, &client_len);
        if (newsockfd < 0) {
            perror("accept");
            exit(1);
        }

        pid = fork();

        if (pid == 0)
        {
            close(0);
            close(1);
            close(2);

            dup(newsockfd);
            dup(newsockfd);
            dup(newsockfd);
            close(newsockfd);

            printf("calling doit\n");
            doit();

            close(0);
            close(1);
            close(2);

            exit(0);
        }

        close(newsockfd);
    }

    return 0; /* Never reached */
}
