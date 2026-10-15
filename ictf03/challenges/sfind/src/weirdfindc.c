/* weirdfind client */
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <errno.h>
#include <stdarg.h>

#ifndef	INADDR_NONE
#define	INADDR_NONE	0xffffffff
#endif	/* INADDR_NONE */

extern int	errno;

int
errexit(const char *format, ...)
{
	va_list	args;

	va_start(args, format);
	vfprintf(stderr, format, args);
	va_end(args);
	exit(1);
}

int
connectsock(const char *host, const char *service, const char *transport )
{
  struct hostent *phe;
  struct servent *pse;
  struct protoent *ppe;
  struct sockaddr_in sin;
  int s, type;
  
  
  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  
  /* Map service name to port number */
  if ((pse = getservbyname(service, transport)))
    sin.sin_port = pse->s_port;
  else if ((sin.sin_port=htons((unsigned short)atoi(service))) == 0)
    errexit("can't get \"%s\" service entry\n", service);
  
  /* Map host name to IP address, allowing for dotted decimal */
  if ((phe = gethostbyname(host)))
    memcpy(&sin.sin_addr, phe->h_addr, phe->h_length);
  else if ( (sin.sin_addr.s_addr = inet_addr(host)) == INADDR_NONE )
    errexit("can't get \"%s\" host entry\n", host);
  
  /* Map transport protocol name to protocol number */
  if ( (ppe = getprotobyname(transport)) == 0)
    errexit("can't get \"%s\" protocol entry\n", transport);
  
  /* Use protocol to choose a socket type */
  if (strcmp(transport, "udp") == 0)
    type = SOCK_DGRAM;
  else
    type = SOCK_STREAM;
  
  /* Allocate a socket */
  s = socket(PF_INET, type, ppe->p_proto);
  if (s < 0)
    errexit("can't create socket: %s\n", strerror(errno));
  
  /* Connect the socket */
  if (connect(s, (struct sockaddr *)&sin, sizeof(sin)) < 0)
    errexit("can't connect to %s.%s: %s\n", host, service,
	    strerror(errno));
  return s;
}

int
connectUDP(const char *host, const char *service )
{
  return connectsock(host, service, "udp");
}

#define	BUFSIZE 65535
int
sendrequest(const char *host, const char *service)
{
  char	buf[BUFSIZE];
  int	s, nchars;
  char ch;
  int i;

  s = connectUDP(host, service);
  
  i = 0;
  while (((ch = getchar()) != EOF) && i < BUFSIZE) 
    {
      buf[i] = ch;
      i++;
    }
  nchars = strlen(buf);
  (void) write(s, buf, nchars);
  
  if ((nchars = read(s, buf, BUFSIZE)) < 0)
    {
      errexit("socket read failed: %s\n",
	      strerror(errno));
    }
  buf[nchars] = '\0';
  printf("%s", buf);
  fflush(stdout);
  return 0;
}

int
main(int argc, char *argv[])
{
	char	*host = "localhost";
	char	*service = "31337";

	switch (argc) {
	case 1:
		host = "localhost";
		break;
	case 3:
		service = argv[2];
		/* FALL THROUGH */
	case 2:
		host = argv[1];
		break;
	default:
		fprintf(stderr, "usage: weridfindc [host [port]]\n");
		exit(1);
	}
	sendrequest(host, service);
	exit(0);
}

