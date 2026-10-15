#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>

char *init = "SPAM-IN-SPAM-OUT";

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
}

void manage_request(u_long client_addr, u_short client_port)
{
  char filename[512];
  char banner[64];
  char command[256];
  char newflag[128];
  char savedflag[128];
  int pop = 123;
  FILE *f = NULL;
  char c;

  if (!fgets(banner, 512, stdin))
    {
      printf("What was THAT?!?!\n");
      fflush(stdout);
      return;
    }

  if (strncmp(banner, init, strlen(init))) 
    {
      printf("Wrong SPAM, man?\n"); 
      fflush(stdout);
      if (pop == 123) {
	printf("I don't believe you just said:\n"); 
	fflush(stdout);
	printf(banner); 
	fflush(stdout);
      }
      return;
    }

  fgets(filename, 512, stdin);

  if (!strcmp(init, "SPAM-IN-SPAM-OUT")) {
    sprintf(command, "tail -n 1 %s", filename);
    fflush(stdout);
    if ((f = popen(command, "r")) == NULL) {
      printf("Yo! You don't want to make me do THAT!?!?\n");
      fflush(stdout);
      return;
    }
    while(fread(&c, 1, 1, f)) {
      putchar(c);
    }
    fflush(stdout);
    pclose(f);
    return;
  }
  else {
    if ((f = fopen(filename, "a+")) == NULL) {
      printf("Hey! That's not the right file!\n");
      fflush(stdout);
      return;
    }
    while(fgets(newflag, 512, f)) {
      strcpy(savedflag, newflag);
    }
    printf(savedflag);
    fflush(stdout);
    fclose(f);
    return;
  }
  return;
}


int main(int argc, char *argv[]) 
{
  struct sockaddr_in server_addr;
  struct sockaddr_in client_addr;
  int sockfd, newsockfd;
  unsigned int client_len;
  int port;
  int on = 1;
  int pid;

  if (argv[1] != NULL)
    {
      port = atoi(argv[1]);
    }
  else
    {
      port = 8009;
    }

  bzero((char *) &server_addr, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);
  server_addr.sin_addr.s_addr = INADDR_ANY;

  sockfd = socket(PF_INET, SOCK_STREAM, 0);
  if (sockfd == -1) 
    {
      perror("socket");
      exit(1);
    }

  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char *)&on, sizeof(on)) == -1) 
    {
      perror("setsockopt");
      exit(1);
    }

  if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr))) 
    {
      perror("bind");
      exit(1);
    }

  if (listen(sockfd, 5)) 
    {
      perror("listen");
      exit(1);
    }
#ifdef CUTIT
  fprintf(stderr, "%s: using address %s and port %d\n",
	  argv[0],
	  inet_ntoa(server_addr.sin_addr),
	  port);
#endif

  (void) signal(SIGCHLD, reaper);
 
  client_len = sizeof(client_addr);
  while (1)
    {
      newsockfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_len);
      if (newsockfd < 0) 
	{
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
	  manage_request((u_long) (client_addr.sin_addr.s_addr), 
			 (u_short) (client_addr.sin_port));
	    
	  fflush(stdout);
	  close(0);
	  close(1);
	  close(2);
	  
	  exit(0);
	}
      close(newsockfd); 
    }
  
  return 0; /* Never reached */
}
