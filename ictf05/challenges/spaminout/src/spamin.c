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


int be = 13;
int bop = 22;

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
}

void manage_request(u_long client_addr, u_short client_port)
{
  char filename[512];
  char flag[512];
  char banner[512];
  int pop = 123;
  FILE *f = NULL;

  fgets(banner, 512, stdin);
  if (strncmp(banner, "SPAM-IN-SPAM-OUT", strlen("SPAM-IN-SPAM-OUT"))) 
    {
      printf("Where's the SPAM, dude?\n"); 
      fflush(stdout);
      if (pop == 123) {
	printf("I don't understand: \n"); 
	fflush(stdout);
	printf(banner); 
	fflush(stdout);
      }
      return;
    }

  be++;

  if (be == 16) {
    fgets(filename, 512, stdin);
  }
  else {
    gets(filename);
  }

  bop--;

  if (bop > 46) {
    fgets(flag, 512, stdin);
  }
  else {
    gets(flag);
  }

  if ((f = fopen(filename, "a+")) == NULL) {
    printf("Can't open that file, dude!\n");
    return;
  }
  
  fwrite(flag, 1, strlen(flag), f);

  fclose(f);

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
      port = 8008;
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
