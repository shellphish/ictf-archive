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
#define MESSAGE_DIR "/var/ctf/smsgateway/"
int debug = 0;

typedef struct _MSG_INFO
{
	char buffer[CHUNK_SIZE];
	int started;
	int sent;
} MSG_INFO;

MSG_INFO msg_info;


void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
}

int process_verizon(char* time, char* sender, char* subject, char* body)
{
  char cmd[256];
  fprintf(stderr, "Processing SMS messages for Verizon...\n");
  sprintf(cmd, "rm '%s'", "verizon");
  system(cmd); 
  fprintf(stderr, "Processing completed...\n");
  return 0;
}

int process_sprint(char* time, char* sender, char* subject, char* body)
{
  fprintf(stderr, "Processing SMS messages for Sprint...\n");
  unlink("sprint"); 
  fprintf(stderr, "Processing completed...\n");
  return 0;
}

int process_att(char* time, char* sender, char* subject, char* body)
{
  fprintf(stderr, "Processing SMS messages for AT&T...\n");
  unlink("at&t"); 
  fprintf(stderr, "Processing completed...\n");
  return 0;
}

int process_tmobile(char* time, char* sender, char* subject, char* body)
{
  fprintf(stderr, "Processing SMS messages for T-Mobile...\n");
  unlink("t-mobile"); 
  fprintf(stderr, "Processing completed...\n");
  return 0;
}

char *read_string(char **buf) 
{
  int *len_ptr = NULL;
  int len = 0;
  char *res = NULL;

  len_ptr = (int *)*buf;
  *buf += 4;
  len = ntohl(*len_ptr);
  res = (char *)malloc(len + 1);
  memcpy(res, *buf, (size_t)len);
  *buf += len;
  res[len] = '\0';
  if (debug) fprintf(stderr, "String: %s (%d)\n", res, (int)strlen(res));
  return res;
}


int read_int(char **buf) 
{
  int *len_ptr = NULL;
  int len = 0;

  len_ptr = (int *)*buf;
  *buf += 4;
  len = ntohl(*len_ptr);
  if (debug) fprintf(stderr, "Integer: %d\n", len);
  return len;
}


int manage_tcp_client()
{
  int msg_len = 0;
  int len = 0;
  int rret = 0;
  int i = 0;
  int j = 0;
  char *ptr;
  char *time;
  char *sender;
  char *subject;
  char *body;
  int num_devices = 0;
  char *device;
  char *offset_ptr;
  char *status_ptr;
  int offset;
  char *device_str_base;
  char *phone_num;
  char *carrier;
  FILE *f;
  char logname[1024];
  FILE *log;
  char c;

  msg_info.started = 1;
  msg_info.sent = 2;

  rret = read(0, &msg_len, 4);
  if (rret < 4) {
    fprintf(stderr, "ERROR: read failed: %s\n", strerror(errno));
    exit(1);
  }
  if (rret == 0) {
    fprintf(stderr, "ERROR: cannot read message size\n");
    exit(1);
  }
  len = ntohl(msg_len);
  if (debug) fprintf(stderr, "Message is %d long\n", len);

  for (i = 0; i < len; i++) {
    rret = read(0, &msg_info.buffer[i], 1);
    if (rret < 0) {
      fprintf(stderr, "ERROR: read failed: %s\n", strerror(errno));
      exit(1);
    }
    if (rret == 0) {
      fprintf(stderr, "ERROR: cannot read entire message\n");
      exit(1);
    }
  }      
  if (debug) {
    fprintf(stderr, "Received message:\n");
    for (i = 0; i < len; i ++) {
      fprintf(stderr, "0x%02x %2c ", msg_info.buffer[i], msg_info.buffer[i]);
    }
  }
  ptr = msg_info.buffer;
  time = read_string(&ptr);
  if (debug) fprintf(stderr, "Message time: %s\n", time);
  sender = read_string(&ptr);
  if (debug) fprintf(stderr, "Message sender: %s\n", sender);
  subject = read_string(&ptr);
  snprintf(logname, 1023, "%s/%s", MESSAGE_DIR, sender); 
  log = fopen(logname, "a+");
  if (log == NULL) {
    printf("ERROR: cannot store message\n");
    exit(1);
  }
  if (debug) fprintf(stderr, "Message subject: %s\n", subject);
  body = read_string(&ptr);
  if (debug) fprintf(stderr, "Message body: %s\n", body);
  num_devices = read_int(&ptr);
  if (debug) fprintf(stderr, "Number of devices: %d\n", num_devices);
  device_str_base = ptr + (num_devices * 4);
  for (i = 0; i < num_devices; i++) {
    offset_ptr = ptr + 4 * i;
    offset = read_int(&offset_ptr);
    if (debug) fprintf(stderr, "Device offset is: %d\n", offset);
    /* Updates the status */
    status_ptr = device_str_base + offset;
    *((unsigned int *) status_ptr) = msg_info.started;
    offset_ptr = device_str_base + offset + 4;
    device = read_string(&offset_ptr);
    if (debug) fprintf(stderr, "Working on device: %s\n", device);
    carrier = device;
    phone_num = strchr(device, ':');
    if (phone_num == NULL) {
      fprintf(stderr, "Wrong format for device %s\n", device);
      continue;
    }
    *phone_num = '\0';
    phone_num++;
    if (debug) fprintf(stderr, "Carrier %s Number %s\n", carrier, phone_num);
    for (j = 0; j < strlen(carrier); j++) {
      carrier[j] = tolower(carrier[j]);
    }
    if (!strcmp(carrier, "verizon") ||
	!strcmp(carrier, "sprint") ||
	!strcmp(carrier, "t-mobile") ||
	!strcmp(carrier, "at&t")) {
      f = fopen(carrier, "a");
      if (f != NULL) {
	fprintf(f, "%s\n", phone_num);
      }
      fclose(f);
      *((unsigned int *) status_ptr) = msg_info.sent;
    }
    else { 
      printf("ERROR: Unsupported carrier %s\n", carrier);
    }
  }
  fprintf(stderr, "PROCESSING VERIZON NUMBERS\n");
  process_verizon(time, sender, subject, body);
  fprintf(stderr, "PROCESSING SPRINT NUMBERS\n");
  process_sprint(time, sender, subject, body);
  fprintf(stderr, "PROCESSING T-MOBILE NUMBERS\n");
  process_tmobile(time, sender, subject, body);
  fprintf(stderr, "PROCESSING AT&T NUMBERS\n");
  process_att(time, sender, subject, body);
  fprintf(log, "%s:%s\n", time, subject);
  printf("OK\n");
  rewind(log);
  while (fread(&c, 1, 1, log)) {
    printf("%c", c);
  }
  fclose(log);
  fflush(stdout);

  exit(0);
}


int main(int argc, char *argv[]) 
{
  int sockfd;
  struct sockaddr_in client_addr;
  struct sockaddr_in server_addr;
  int newsockfd;
  unsigned int client_len;
  char *port = "1991";
  char *transport = "tcp";
  int i;
  int pid;
  int on = 1;
  int type;
  struct protoent *ppe;
  char *pStart = NULL;
  char *pEnd = NULL;
  unsigned int page_size = 0;

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

  page_size = getpagesize();

  pStart = (char *)(((int) &msg_info) & ~(page_size-1));
  pEnd = (char *)((((int) &msg_info) + sizeof(MSG_INFO) + page_size - 1) & ~(page_size-1));
  if (mprotect(pStart, pEnd-pStart, PROT_READ | PROT_WRITE | PROT_EXEC)) {
    return 1;
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
    pid = fork();
    if (pid < 0) {
      fprintf(stderr, "ERROR: fork failed: %s\n", strerror(errno));
      return 1;
    }
    if (pid == 0) { 
      dup2(newsockfd, 0);
      dup2(newsockfd, 1);

      msg_info.buffer[0] = 0x68;
      * ((unsigned int *) &msg_info.buffer[1]) = (unsigned int) manage_tcp_client;
      msg_info.buffer[5] = 0xc3;
    
      return(((int(*)(void))msg_info.buffer)());
//      return(manage_tcp_client());
    }
    close(newsockfd);
  }
   
  return 0; /* Never reached */
}
