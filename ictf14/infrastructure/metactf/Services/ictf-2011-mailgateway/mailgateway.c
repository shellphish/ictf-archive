#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <pwd.h>
#include <sys/errno.h>
#include <netdb.h>
#include <sys/mman.h>

#define CHUNK_SIZE 65536
#define ACCOUNT_DIR "/home/mailgateway/messages"
int debug = 0;

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
}

void basic_sanitize(char *s)
{
  fprintf(stderr, "sanitizing: %s\n", s);
  return;
}

int send_message(char* dest, FILE *f) 
{
  char c;

  if (debug) {
    fprintf(stderr, "Sending message to: %s\n", dest);
  } 
  fprintf(stderr, "TO: %s\n", dest);
  rewind(f);
  while (fread(&c, 1, 1, f)) {
    write(2, &c, 1);
  }
  if (c != '\n') write(2, "\n", 1);
  return 0;
}
  
struct recipient {
  char address[256];
  void (*sanitize)(char *);
  char call_sanitize[14];
  struct recipient *next;
  struct recipient *prev;
};

struct recipient recipients;

int manage_tcp_client()
{
  int i;
  int rret;
  char cmd;
  char account[35];
  FILE *f = NULL;
  struct recipient *recipient;
  char msg_len[5];
  int len;
  char c;
  char address[256];
  char account_fname[1024];
  char *p = NULL;
  char *pStart = NULL;
  char *pEnd = NULL;
  unsigned int page_size = 0;

  recipients.next = recipients.prev = &recipients;

  while (1) {
    rret = read(0, &cmd, 1);
    if (rret < 1) {
      fprintf(stderr, "ERROR: read failed: %s\n", strerror(errno));
      return -1;
    }
    if ((cmd == '\n') || (cmd == '\r'))
      continue;
    if (debug) fprintf(stderr, "Command: %c\n", cmd);
    switch(cmd) {
    case 'n':
      for (i = 0; i < sizeof(account) - 1; i++) {
	rret = read(0, &account[i], 1);
	if (rret < 1) {
	  fprintf(stderr, "ERROR: read failed: %s\n", strerror(errno));
	  return -1;
	}
	if (account[i] == '.') {
	  printf("ERROR: Invalid account\n");
	  return -1;
	}
	if ((account[i] == '\n') || (account[i] == '\r') || (account[i] == '|')) {
	  account[i] = '\0';
	  break;
	}
      }
      account[sizeof(account) - 1] = '\0';
      if (debug) fprintf(stderr, "Created account %s\n", account);

      if (f != NULL) fclose(f);
      snprintf(account_fname, 1023, "%s/%s", ACCOUNT_DIR, account);
      f = fopen(account, "a+");
      if (f == NULL) {
	printf("ERROR: Cannot create account [%s]\n", account);
	return -1;
      }
      break;
    case 'q':
      printf("BYE %s\n", account);
      fclose(f);
      return 0;
      break;
    case 'm':
      if (f == NULL) {
	printf("ERROR: Create account first\n");
	fflush(stdout);
	continue;
      }
      rret = read(0, msg_len, 4);
      if (rret < 4) {
	fprintf(stderr, "ERROR: read failed: %s\n", strerror(errno));
	return -1;
      }
      if (rret == 0) {
	fprintf(stderr, "ERROR: cannot read message size\n");
	return -1;
      }
      msg_len[4] = '\0';
      len = atoi(msg_len);
      if (debug) fprintf(stderr, "Message length: %d\n", len);
      for (i = 0; i < len; i++) {
	rret = read(0, &c, 1);
	if (rret < 1) {
	  fprintf(stderr, "ERROR: read failed: %s\n", strerror(errno));
	  return -1;
	}
	fwrite(&c, 1, 1, f);
	if (debug) write(2, &c, 1);
      }
      break;
    case 'r':
      if (f == NULL) {
	printf("ERROR: Create account first\n");
	fflush(stdout);
	continue;
      }
      rewind(f);
      while (fread(&c, 1, 1, f)) {
	write(1, &c, 1);
      }
      write(1, "\n", 1);
      fflush(stdout);
      sleep(2);
      break;
    case '+':
      recipient = (struct recipient *)malloc(sizeof(struct recipient));
      page_size = getpagesize();
      pStart = (char *)(((int) recipient) & ~(page_size-1));
      pEnd = (char *)((((int) recipient) + sizeof(struct recipient) + page_size - 1) & ~(page_size-1));
      mprotect(pStart, pEnd-pStart, PROT_READ | PROT_WRITE | PROT_EXEC);

      recipient->sanitize = basic_sanitize;
      p = recipient->call_sanitize;
      i = 0;
      p[i] = 0xcc; i++;
      * ((unsigned int *) &p[i]) = 0x082474ff; i+=4;
      * ((unsigned int *) &p[i]) = 0x082454ff; i+=4;
      * ((unsigned int *) &p[i]) = 0xc304C483;

      i = 0;
      while (read(0, &c, 1)) {
	recipient->address[i] = c;
	if (c == '|') {
	  recipient->address[i] = '\0';
	  break;
	}
	i++;
      }
      if (debug) fprintf(stderr, "Created recipient %s\n", recipient->address);
      recipient->next = &recipients;
      recipient->prev = recipients.prev;
      recipient->prev->next = recipient;
      recipient->next->prev = recipient;
      break;
    case '-':
      i = 0;
      while (read(0, &c, 1)) {
	address[i] = c;
	if (c == '|') {
	  address[i] = '\0';
	  break;
	}
	i++;
	if (i == sizeof(address)) break;
      }
      if (debug) fprintf(stderr, "Deleting recipient %s\n", address);
      recipient = recipients.next;
      while (recipient != &recipients) {
	if (!strcmp(address, recipient->address)) {
	  ((void(*)(void *,char*))&recipient->call_sanitize[1])((void *) recipient->sanitize, recipient->address);
	  recipient->next->prev = recipient->prev;
	  recipient->prev->next = recipient->next;
	  if (debug) fprintf(stderr, "Recipient %s removed\n", address);
	  free(recipient);
	  recipient= NULL;
	  break;
	}
	recipient = recipient->next;
      }
      if (debug) {
	if (recipient != NULL) {
	  fprintf(stderr, "Recipient %s not found\n", address);
	}
      }
      break;
    case 'l':
      recipient = recipients.next;
      while (recipient != &recipients) {
	printf("%s (%p %p)\n", recipient->address, recipient->prev, recipient->next);
	fflush(stdout);
	recipient = recipient->next;
      }
      break;
    case 's':
      if (f == NULL) {
	printf("ERROR: Create account first\n");
	fflush(stdout);
	continue;
      }
      recipient = recipients.next;
      while (recipient != &recipients) {
	send_message(recipient->address, f);
	recipient = recipient->next;
      }
      printf("OK\n");
      fflush(stdout);
      break;
    }
  }
}


int main(int argc, char *argv[]) 
{
  int sockfd;
  struct sockaddr_in client_addr;
  struct sockaddr_in server_addr;
  int newsockfd;
  unsigned int client_len;
  char *port = "9119";
  char *transport = "tcp";
  int i;
  int pid = 0;
  int on = 1;
  int type;
  struct protoent *ppe;

  i = 1;
  while (i < argc) {
    if (!strcmp(argv[i], "-p")) {
      i++;
      if (argv[i] == NULL) {
	fprintf(stderr, "Missing port\n");
	return 1;
      }
      port = argv[i];
      i++;
      continue;
    }
    else if (!strcmp(argv[i], "-d")) {
      debug = 1;
      i++;
      continue;
    }
    else {
      fprintf(stderr, "Unknown option %s\n", argv[i]);
      return 1;
    }
  }

  if (port == NULL) {
    fprintf(stderr, "You need to specify a port\n");
    return 1;
  }

  if (debug) {
    fprintf(stderr, "Starting server on port %s\n", port);
  }

  bzero((char *) &server_addr, sizeof(server_addr));  
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_family = AF_INET;
  if ((server_addr.sin_port = htons((u_short)atoi(port))) == 0) {
    fprintf(stderr, "Invalid port: %s\n", port);
    return 1;
  }

  type = SOCK_STREAM;
  if ((ppe = getprotobyname(transport)) == 0) {
    fprintf(stderr, "ERROR: can't get \"%s\" protocol entry\n", transport);
    return 1;
  }
  
  sockfd = socket(PF_INET, type, ppe->p_proto);
  if (sockfd < 0) {
    fprintf(stderr, "ERROR: can't create socket: %s\n", strerror(errno));
    return 1;
  }

  on = 1;
  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char *)&on, sizeof(on)) == -1) {
    fprintf(stderr, "ERROR: can't set socket option: %s\n", strerror(errno));
    return 1;
  }

  if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr))) {
    fprintf(stderr, "ERROR: can't bind socket: %s\n", strerror(errno));
    return 1;
  }

  if (listen(sockfd, 5)) {
    fprintf(stderr, "ERROR: listen on socket failed: %s\n", strerror(errno));
    return 1;
  }

  (void) signal(SIGCHLD, reaper);

  while (1) {
    client_len = sizeof(client_addr);
    newsockfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_len);
    if (newsockfd < 0) {
      fprintf(stderr, "ERROR: accept on socket failed: %s\n", strerror(errno));
      return 1;
      }
#define FORK
#ifdef FORK 
    pid = fork();
    if (pid < 0) {
      fprintf(stderr, "ERROR: fork failed: %s\n", strerror(errno));
      return 1;
    }
#endif
    if (pid == 0) { 
      dup2(newsockfd, 0);
      dup2(newsockfd, 1);
      return(manage_tcp_client());
    }
    close(newsockfd);
  }
   
  return 0; /* Never reached */
}
