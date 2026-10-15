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

#define DEBUG  
#define DEFAULT_PORT 1969
#define KEY "F2654hD4"
#define MAXSIZE 512

int main(int argc, char *argv[]) 
{
  char *wwid = NULL;
  char *vote = NULL;
  char *host = NULL;
  int port = DEFAULT_PORT;
  struct sockaddr_in server_addr;
  struct hostent *phe = NULL;
  int sock = 0;
  char *request = NULL;
  int count = 0;
  char reply[MAXSIZE];
  int i;
  int j;
  char *key = KEY;
  char code[16];
  int reqlen = 0;


  i = 1;
  while (i < argc)
    {
      if (!strcmp(argv[i], "--wwid"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing world-wide id\n");
	      exit(1);
	    }
	  wwid = argv[i];
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "--vote"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing vote\n");
	      exit(1);
	    }
	  vote = argv[i];
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "--host"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing votecast server name\n");
	      exit(1);
	    }
	  host = argv[i];
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "--port"))
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
      else
	{
	  fprintf(stderr, "Unknown option %s\n", argv[i]);
	  exit(1);
	}
    }

  if ((wwid == NULL) || (vote == NULL) || (host == NULL))
    {
      fprintf(stderr, "Missing parameter\n");
      return -1;
    }

#ifdef DEBUG
  fprintf(stderr, "Casting vote to %s:%d for %s: %s\n",
	  host,
	  port,
	  wwid,
	  vote);
#endif

  bzero((char *) &server_addr, sizeof(server_addr));  
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);

  if ((phe = gethostbyname(host)))
    {
      memcpy(&server_addr.sin_addr, phe->h_addr, phe->h_length);
    }
  else if ((server_addr.sin_addr.s_addr = inet_addr(host)) == INADDR_NONE)
    {
      fprintf(stderr, "Cannot find destination host \"%s\"\n", host);
      return -1;
    }

  sock = socket(PF_INET, SOCK_STREAM, 0);
  if (sock < 0) 
    {
      perror("socket");
      return -1;
    }
  if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) 
    {
      perror("connect") ;
      return -1;
    }

  count = strlen(wwid) + strlen(vote) + strlen("! ") + 1;
  request = malloc(count);
  if (request == NULL)
    {
      perror("malloc");
      return -1;
    }
  if (strlen(request) > 512)
    {
      fprintf(stderr, "Request may be too big for server... aborting\n");
      return -1;
    }
  snprintf(request, count, "!%s %s", wwid, vote); 
  reqlen = strlen(request);

  for (i = 0; i < reqlen; i++)
    {
      j = i % strlen(key);
      request[i] = request[i] ^ key[j];
    }

  fprintf(stderr, "Sending vote: ");
  for (i = 0; i < reqlen; i++)
    {
      fprintf(stderr, "%02X", request[i]);
      sprintf(code, "%02X", request[i]);
      if (write(sock, code, strlen(code)) < strlen(code))
	{
	  perror("write");
	  return -1;
	}
    }
  fprintf(stderr, "\n");
  shutdown(sock, 1);

  i = 0;
  reply[0] = '\0';
  while (1) 
    {
      if (i == (MAXSIZE - 1)) 
	{
	  fprintf(stderr, "KO Reply is too long\n");
	  return -1; 
	}
      count = read(sock, &(reply[i]), 1) ;
      if (count < 0)
	{
	  fprintf(stderr, "An error occured reading the reply\n");
	  return -1;
	}
      else if (count == 0)
	{
	  break;
	}
      i++;
    }
  reply[i] = '\0';

  fprintf(stderr, "Received reply: %s", reply);  
  return 0;
}
