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
#include <sys/wait.h>

#define BUFSIZE 512
#define USERDIR "userdict"
#define MAXWORD 64
#define DEFAULT_PORT 11111

char *dict = "/usr/share/dict/words";

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
   
}

void verify_password()
{
  char storedword[MAXWORD];
  char buffer[BUFSIZE];
  char userdict[BUFSIZE];
  char checkstr[BUFSIZE];
  char *username = NULL;
  char *command = NULL;
  char *arglist = NULL;
  char *password = NULL;
  char *word = NULL;
  char *dictword = NULL;
  int i;
  int numc;
  int result; 
  FILE *file = NULL;
  char *p;
  struct stat info;

  if (stat(USERDIR, &info) == -1)
    {
      if (mkdir(USERDIR, 0) == -1)
	{
	  perror("mkdir");
	  return;
	}
    }
  if (chmod(USERDIR, S_IRWXU) == -1)
    {
      perror("chmod");
      return;
    }

  i = 0;
  while((numc = read(0, &(buffer[i]), 1)) == 1)
    {
      /* Checks for CR-LF or just LF so that it works
	 with both telnet and nc */
      if (buffer[i] == '\n')
	{
	  if (buffer[i - 1] == '\r') buffer[i - 1] = '\0';
	  else buffer[i] = '\0';
	  break;
	}
      i++;
      if (i == (BUFSIZE - 1))
	{
	  buffer[BUFSIZE - 1] = '\0';
	  break;
	}
    }

  p = strchr(buffer, ' ');

  if (p == NULL) 
    { 
      printf("ERROR: wrong format\n"); 
      return;
    }
  
  *p = '\0';

  command = buffer;

  username = p + 1;
  
  p = strchr(username, ' ');

  if (p != NULL) 
    { 
      *p = '\0';
      arglist = p + 1;
    }
  else
    {
      arglist = NULL;
    }

  if (!strcmp(command, "CHECK"))
    {
      sprintf(userdict, "%s/%s", USERDIR, username);
      file = fopen(userdict, "r");
      if (file == NULL)
	{
	  fprintf(stdout, "ERROR: cannot find user's dict file\n");
	  return;
	}
      password = arglist;
      sprintf(checkstr, "grep %s %s/%s > /dev/null", password, USERDIR, username);
      result = system(checkstr);
      if (result == 0)
	{
	  printf("This password sucks!\n");
	  return;
	}
      sprintf(checkstr, "grep %s %s > /dev/null", password, dict);
      result = system(checkstr);
      if (result == 0)
	{
	  printf("This password sucks!\n");
	  return;
	}
      printf("Password is really unbreakable!\n");
      return;
    }
  else if (!strcmp(command, "STORE"))
    {
      sprintf(userdict, "%s/%s", USERDIR, username);
      file = fopen(userdict, "a");
      if (file == NULL)
	{
	  fprintf(stdout, "ERROR: cannot write to user dict file\n");
	  return;
	}
      word = arglist;
      while (p != NULL)
	{
	  p = strchr(word, ' ');
	  if (p != NULL)
	    {
	      *p = '\0';
	      dictword = word;
	      word = p + 1;
	    }
	  else
	    {
	      dictword = word;
	    }
	  fprintf(file, "%s\n", dictword);
	  fprintf(stdout, "Word \"%s\" included in user dictionary\n", dictword);
	}
      fclose(file);

    }
  else if (!strcmp(command, "DICT"))
    {
      sprintf(userdict, "%s/%s", USERDIR, username);
      file = fopen(userdict, "r");
      if (file == NULL)
	{
	  fprintf(stdout, "ERROR: cannot read from user dict file\n");
	  return;
	}
      i = 0;
      while (1)
	{
	  if (fgets(storedword, BUFSIZE, file) == NULL)
	    {
	      break;
	    }
	  printf(storedword);
	}
    }
  else
    {
      printf("ERROR: unknown command\n");
    }

  return;
}

int main(int argc, char *argv[]) 
{
  struct sockaddr_in server_addr;
  struct sockaddr client_addr;
  int sockfd, newsockfd, client_len;
  int port = DEFAULT_PORT;
  int pid;
  int on = 1;
  int i;

  i = 1;
  while (i < argc)
    {
      if (!strcmp(argv[i], "--port"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing port\n");
	      exit(1);
	    }
	  port = atoi(argv[i]);
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "--dict"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing dictionary file\n");
	      exit(1);
	    }
	  dict = argv[i];
	  i++;
	  continue;
	}
      else
	{
	  fprintf(stderr, "Unknown option %s\n", argv[i]);
	  exit(1);
	}
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
      return -1;
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

  (void) signal(SIGCHLD, reaper);

  while (1)
    {
      client_len = sizeof(client_addr);
      newsockfd = accept(sockfd, &client_addr, &client_len);
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
	  
	  verify_password();
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
