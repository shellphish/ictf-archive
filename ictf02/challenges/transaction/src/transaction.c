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
#include <curses.h>

void manage_request(u_long client_addr, u_short client_port)
{
  char buffer[64];
  char *cmd;
  int i, numc;
  char pass[256];

  i = 0;
  while((numc = read(0, &(buffer[i]), 1)) == 1)
    {
      if (buffer[i] == '\n')
	{
	  if (buffer[i - 1] == '\r') buffer[i - 1] = '\0';
	  else buffer[i] = '\0';
	  break;
	}
      i++;
    }

  if (numc == 0)
    {
      perror("read");
      return;
    }

  if (!strncmp(buffer, "HELP", strlen("HELP")))
    {
      printf("Command summary\n");
      printf("HELP - Print this message\n");
      printf("PAYCHECK - Perform a paycheck operation\n");
      printf("FILE - Print a file in the filesystem\n");
      fflush(stdout);
    }
  else if  (!strncmp(buffer, "PAYCHECK", strlen("PAYCHECK")))
    {
      printf("Executing paycheck operation\n");
      printf("Please insert paycheck password\n");
      fflush(stdout);

      gets(pass);
      printf(pass);
      fflush(stdout);

      if (strncmp(pass, "banana", strlen("banana")))
	{
	  printf("Wrong password. Bye.\n");
	  fflush(stdout);
	  return;
	}
      printf("Executing paycheck operation... This may take some time\n");
      fflush(stdout);
      sleep(5); /* Execute Shell script here */
      system("./transaction.pl");
      printf("The funds have been transferred to employees accounts\n");
      printf("All your base are belong to us...\n");
    }
  else if  (!strncmp(buffer, "FILE", strlen("FILE")))
    {
      cmd = malloc(strlen(buffer));
      sprintf(cmd, "cat %s", buffer + 5);
      printf("Executing command \"%s\"\n", cmd);
      fflush(stdout);
      system(cmd);
    }
  else
    {
      fprintf(stderr, "Malformed request %s. Use HELP\n", buffer);
    }

  fflush(stdout);
  fflush(stderr);
  return;
}

int main(int argc, char *argv[]) 
{
  struct stat fileinfo;
  char command[512];
  char docname[512];
  FILE *docfile;
  struct sockaddr_in server_addr;
  struct sockaddr_in client_addr;
  int sockfd, newsockfd, client_len, server_len;
  int port;

  if (argv[1] != NULL)
    {
      port = atoi(argv[1]);
    }
  else
    {
      port = 7979;
    }

  bzero((char *) &server_addr, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);
  server_addr.sin_addr.s_addr = INADDR_ANY;

  fprintf(stderr, "%s: using address %s and port %d\n",
	  argv[0],
	  inet_ntoa(server_addr.sin_addr),
	  port);

  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd == -1) 
    {
      perror("socket");
      exit(1);
    }

  server_len = sizeof(server_addr);
  if (bind(sockfd, (struct sockaddr *)&server_addr, server_len)) 
    {
      perror("bind");
      exit(1);
    }

  if (listen(sockfd, 5)) 
    {
      perror("listen");
      exit(1);
    }

  client_len = sizeof(client_addr);
  while (1)
    {
      newsockfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_len);
      if (newsockfd < 0) 
	{
	  perror("accept");
	  exit(1);
	}
  
      close(0);
      close(1);
      close(2);
      
      dup(newsockfd);
      dup(newsockfd);
      dup(newsockfd);
      close(newsockfd);
      manage_request((u_long) (client_addr.sin_addr.s_addr), 
		     (u_short) (client_addr.sin_port));
      shutdown(0, 2);
      
    }
  exit(0);
}




