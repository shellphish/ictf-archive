#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <unistd.h>
#include <ctype.h>

#include <netinet/in.h>
#include <arpa/inet.h>

#include <netdb.h>
#include <string.h>
#include "mydiag.h"

#ifndef	INADDR_NONE
#define	INADDR_NONE	0xffffffff
#endif	/* INADDR_NONE */

#include "zocket.h"

#define DEBUG

int
connectsock(const char *host, const char *service, const char *transport)
{
  struct hostent *phe; /* pointer to host information entry */
  struct servent *pse; /* pointer to service information entry	*/
  struct protoent *ppe;	/* pointer to protocol information entry*/
  struct sockaddr_in sin; /* an Internet endpoint address */
  int type; /* socket type */
  int s; /* socket descriptor */

  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;

  /* Map service name to port number */
  if ((pse = getservbyname(service, transport)))
    {
      sin.sin_port = pse->s_port;
    }
  else if ((sin.sin_port = htons((u_short)atoi(service))) == 0)
    {
      my_error(__FILE__, __LINE__, "can't get \"%s\" service entry\n", 
		service);
      return -1;
    }

  /* Map host name to IP address, allowing for dotted decimal */
  if ((phe = gethostbyname(host)))
    {
      memcpy(&sin.sin_addr, phe->h_addr, phe->h_length);
    }
  else if ((sin.sin_addr.s_addr = inet_addr(host)) == INADDR_NONE)
    {
      my_error(__FILE__, __LINE__, "can't get \"%s\" host entry\n", host);
      return -1;
    }

  /* Use protocol to choose a socket type */
  if (strcmp(transport, "udp") == 0)
    {
      type = SOCK_DGRAM;
    }
  else if (strcmp(transport, "tcp") == 0)
    {
      type = SOCK_STREAM;
    }
  else
    {
      my_error(__FILE__, __LINE__, "unknown transport protocol \"%s\"\n", 
		transport);
      return -1;
    }
      

  /* Map transport protocol name to protocol number */
  if ((ppe = getprotobyname(transport)) == 0)
    {
      my_error(__FILE__, __LINE__, "can't get \"%s\" protocol entry\n", transport);
      return -1;
    }
  
 
  /* Allocate a socket */
  s = socket(PF_INET, type, ppe->p_proto);
  if (s < 0)
    {
      my_error(__FILE__, __LINE__, "can't create socket: %s\n", strerror(errno));
      return -1;
    }

  /* Connect the socket */
  if (connect(s, (struct sockaddr *)&sin, sizeof(sin)) < 0)
    {
      my_error(__FILE__, __LINE__, "can't connect to %s.%s: %s\n", 
		host, service, strerror(errno));
      return -1;
    }

  return s;
}

int
connectTCP(const char *host, const char *service)
{
  return connectsock(host, service, "tcp");
}


int 
connectUDP(const char *host, const char *service)
{
  return connectsock(host, service, "udp");
}
 

int 
passivesock(const char *service, const char *transport)
{
  struct servent *pse; /* pointer to service information entry */
  struct protoent *ppe; /* pointer to protocol information entry */
  struct sockaddr_in sin; /* an Internet endpoint address */
  int s, type; /* socket descriptor and socket type */
  int qlen = 5;
  int on = 1;

  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = INADDR_ANY;

  /* Map service name to port number */
  if ((pse = getservbyname(service, transport)))
    {
      sin.sin_port = htons(ntohs((unsigned short)pse->s_port));
    }
  else if ((sin.sin_port=htons((unsigned short)atoi(service))) == 0)
    {
      my_error(__FILE__, __LINE__, "can't get \"%s\" service entry\n", service);
      return -1;
    }

  /* Map protocol name to protocol number */
  if ((ppe = getprotobyname(transport)) == 0)
    {
      my_error(__FILE__, __LINE__, "can't get \"%s\" protocol entry\n", transport);
      return -1;
    }

  /* Use protocol to choose a socket type */
  if (strcmp(transport, "udp") == 0)
    type = SOCK_DGRAM;
  else if (strcmp(transport, "tcp") == 0)
    type = SOCK_STREAM;
  else
    {
      my_error(__FILE__, __LINE__, "unknown protocol \"%s\"\n", transport);
      return -1;
    }

  /* Allocate a socket */
  s = socket(PF_INET, type, ppe->p_proto);
  if (s < 0)
    {
      my_error(__FILE__, __LINE__, "can't create socket: %s\n", strerror(errno));
      return -1;
    }

  /* Use REUSEADDR */
  on = 1;
  if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &on, sizeof (int)))
    {
      my_error(__FILE__, __LINE__, "can't reuse address: %s\n", strerror(errno));
      return -1;
    }

  /* Bind the socket */
  if (bind(s, (struct sockaddr *)&sin, sizeof(sin)) < 0)
    {
      my_error(__FILE__, __LINE__, "can't bind to %s port: %s\n", service,
		strerror(errno));
      return -1;
    }

  if (type == SOCK_STREAM && listen(s, qlen) < 0)
    {
      my_error(__FILE__, __LINE__, "can't listen on %s port: %s\n", service,
		strerror(errno));
      return -1;
    }

  return s;
}


int 
passiveTCP(const char *service)
{
  return passivesock(service, "tcp");
}


int 
passiveUDP(const char *service)
{
  return passivesock(service, "udp");
}


#define LINE_SIZE 512

char *getline_nocrlf(int s)
{
  char *line = NULL;
  char *str = NULL;
  int ret = 0;
  int line_size = 0;
  int index = 0;
  int i = 0;
  char c;
  
  if ((line = (char *)malloc(LINE_SIZE)) == NULL)
    {
      my_error(__FILE__, __LINE__, "malloc failed");
      return NULL;
    }
  
  line_size = LINE_SIZE;
  index = 0;
  c = '\0';

  while (c != '\n')
    {
      ret = read(s, &c, 1);
      /* EOF */
      if (ret == 0)
	{
	  break;
	}
      /* ERROR */
      if (ret < 0)
	{
	  free(line);
	  return NULL;
	}
  
      line[index] = c;
      index++;
      line[index] = '\0';

      if (index == line_size - 2)
	{
	  line_size += LINE_SIZE;
	  if ((line = (char *)realloc(line, line_size)) == NULL)
	    {
	      my_error(__FILE__, __LINE__, "realloc failed");
	      return NULL;
	    }
	}
    }
  
  for (i = index - 1; i >= 0; i--)
    {
      if ((line[i] != '\n') && (line[i] != '\r')) break;
	  
      line[i] = '\0';
    }

  str = strdup(line);
  free(line);
  return str;

}
 
