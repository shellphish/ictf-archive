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
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <ctype.h>
#include <arpa/inet.h>
#define CREDITS "Written by z4n4rd1"
#define DEFAULT_PORT 1969
#define KEY "F2654hD4"
#define VOTEDIR "votes"
#define MAXSIZE 512

int maxsize = 0;
int debug = 0;

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
   
}

void manage_request()
{
  char buf[MAXSIZE];
  char request[MAXSIZE];
  char code[4];
  char *key = KEY;
  char wwid[MAXSIZE];
  char vote[MAXSIZE];
  char previous[MAXSIZE];
  char logfilename[MAXSIZE];
  char cmd[MAXSIZE];
  int logfile;
  int i;
  int count;
  int j;
  int k;
  char ch;
  int num;
  int prevlen;
  FILE *f = NULL;

  if (debug)
    {
      fprintf(stderr, "Processing a new vote\n");
    }

  /* Reads the request */
  i = 0;
  buf[0] = '\0';
  while (1) 
    {
      if ((maxsize != 0) && (i == maxsize - 1))
	{
	  break;
	}
      count = read(0, &(buf[i]), 1) ;
      if (count < 0)
	{
	  fprintf(stdout, "KO Error reading the request\n");
	  return;
	}
      else if (count == 0)
	{
	  break;
	}
      i++;
    }
  buf[i] = '\0';

  if (debug)
    {
      fprintf(stderr, "Received vote: %s\n", buf);
    }
  /* Decode the request */
  k = 0;
  for (i = 0; i < strlen(buf); i = i + 2)
    {
      code[0] = buf[i]; 
      code[1] = buf[i + 1]; 
      code[2] = '\0'; 
      num = (int) strtol(code, NULL, 16);
      j = k % strlen(key);
      request[k] = num ^ key[j];
      k++;
    }

  if (debug)
    {
      fprintf(stderr, "Decrypted request: [%s]\n", request);  
    }

  /* Checks if the request decrypted correctly */
  if ((request[0] != '!') && (request[0] != '#'))
    {
      fprintf(stdout, "KO could not decrypt\n");
      return;
    }

  if (request[0] == '#')
    {
      if (debug)
	{
	  fprintf(stdout, "DEBUG: checking vote %s\n", 
		  &(request[1]));
	}
      sprintf(cmd, "cat %s/%s", VOTEDIR, &(request[1]));
      f = popen(cmd, "r"); 
      if (f == NULL)
	{
	  fprintf(stdout, "KO could not execute command");
	  return;
	}
      while ((ch = fgetc(f)) != EOF)
	{
	  fputc(ch, stdout);
	}
      fputc('\n', stdout);
      return;
    }

  /* Parses the request */
  wwid[0] = '\0';
  vote[0] = '\0';
  sscanf(&(request[1]), "%s %s", wwid, vote);
  if (debug)
    {
      fprintf(stderr, "Request parsed: wwid [%s] vote [%s]\n", wwid, vote);
    }

  /* Checks the request */
  if ((strlen(wwid) == 0) || (strlen(vote) == 0))
    {
      fprintf(stdout, "KO unrecognized format\n");
      return;
    }
      
  snprintf(logfilename, sizeof(logfilename), "%s/%s", VOTEDIR, wwid);

  /* Checks if the vote already exists */
  previous[0] = '\0';
  logfile = open(logfilename, O_RDONLY);
  if (logfile >= 0)
    {
      count = read(logfile, previous, sizeof(previous));
      if (count <= 0)
	{
	  previous[0] = '\0';
	}
      close(logfile);
    }

  /* Creates a new file */
  if ((logfile = open(logfilename, O_WRONLY | O_CREAT | O_TRUNC, 
		      S_IREAD | S_IWRITE | S_IEXEC | 
		      S_IRGRP | S_IXGRP |
		      S_IROTH | S_IXOTH)) < 0) 
    {
      fprintf(stdout, "KO cannot store vote\n");
      return ;
    }  
  write(logfile, vote, strlen(vote));
  close(logfile);

  /* Sends the previous vote back */
  prevlen = strlen(previous);
  if (prevlen)
    {
      fprintf(stdout, "OK ");
      for (i = 0; i < prevlen; i++)
	{
	  j = i % strlen(key);
	  previous[i] = previous[i] ^ key[j];
	  fprintf(stdout, "%02X", previous[i]);
	}
      fprintf(stdout, "\n");
    }
  else
    {
      fprintf(stdout, "OK\n");
    }
  return;
}

int main(int argc, char *argv[]) 
{
  struct stat info;

  int port = DEFAULT_PORT;
  struct sockaddr_in server_addr;
  struct sockaddr client_addr;
  int client_len = 0;
  int ssock = 0;
  int csock = 0;
  int i;
  int on = 1;
  int pid;

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
      else if (!strcmp(argv[i], "--size"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing limit\n");
	      exit(1);
	    }
	  maxsize = atoi(argv[i]);
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "--debug"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing debug code\n");
	      exit(1);
	    }
	  debug = atoi(argv[i]);
	  i++;
	  continue;
	}
      else
	{
	  fprintf(stderr, "Unknown option %s\n", argv[i]);
	  exit(1);
	}
    }

  if (stat(VOTEDIR, &info) == -1)
    {
      if (mkdir(VOTEDIR, 0) == -1)
	{
	  perror("mkdir");
	  return -1;
	}
    }
  if (chmod(VOTEDIR, S_IWUSR | S_IXUSR) == -1)
    {
      perror("chmod");
      return -1;
    }

  if (debug)
    {
      fprintf(stderr, "Votecast server starting (%s)\n", CREDITS);
    }
  bzero((char *) &server_addr, sizeof(server_addr));  
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);


  ssock = socket(PF_INET, SOCK_STREAM, 0);
  if (ssock < 0) 
    {
      perror("socket");
      return -1;
    }
   if (setsockopt(ssock, SOL_SOCKET, SO_REUSEADDR, (char *)&on, sizeof(on)) == -1) 
    {
      perror("setsockopt");
      return -1;
    }
  
  if (bind(ssock, (struct sockaddr *)&server_addr, sizeof(server_addr))) 
    {
      perror("bind");
      return -1;
    }
  
  if (listen(ssock, 5)) 
    {
      perror("listen");
      return -1;
    }
  
  (void) signal(SIGCHLD, reaper);

  while (1)
    {
      client_len = sizeof(client_addr);
      if (debug)
	{
	  fprintf(stderr, "Waiting for votes...\n");
	}
      csock = accept(ssock, &client_addr, &client_len);
      if (csock < 0) 
	{
	  perror("accept");
	  return -1;
	}

      pid = fork();
      
      if (pid == 0)
	{ 
	  close(0);
	  close(1);
	  
	  dup(csock);
	  dup(csock);
	  close(csock);
	  close(ssock);
	  
	  manage_request();
	  fflush(stdout);
	  if (debug)
	    {
	      fprintf(stderr, "Finished processing vote\n");
	    }
	  close(0);
	  close(1);
	  
	  return 0;
	}

      close(csock);
    }

  return 0; /* Never reached */
}
