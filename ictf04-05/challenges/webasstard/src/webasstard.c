#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <sys/types.h>
#ifdef HAVE_DIRENT_H
#include <dirent.h>
#else
#include <sys/dirent.h>
#endif
#include <sys/dir.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/uio.h>
#include <ctype.h>
#include <assert.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <netdb.h>

extern int h_errno;

#include <mydiag.h>
#include <zocket.h>

#ifndef MAXHOSTNAMELEN
#define MAXHOSTNAMELEN 256
#endif

/*
 * DEFINES
 */
#define DEBUG
#define ITERATIVE  
#define BUFSIZE 8192
#define REPLYSIZE 8192
#define DEFAULT_SSL_PORT "4443"
#define DEFAULT_UDP_PORT "2345"
#define DEFAULT_DOCDIR "webdocs"
#define DEFAULT_CONFFILE "webasstard.conf"
#define MAX_QUERY_SIZE 65536
#define REQUEST_HTTPS 1
#define REQUEST_QUERY 2
#define DEFAULT_TIMEOUT 5
#define DEFAULT_CERT_FILE  "webasstard.pem"
#define DEFAULT_KEY_FILE "webasstard.key"
#define ACCEPT_FAILURE_THRESHOLD 100
#define CHUNK_SIZE 512
#define LINE_SIZE 512

/* Parameters: protocol */
#define BAD_REQUEST_REPLY "%s 400 Bad Request\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Error 400 - Bad Request</title></head>\n\
  <body><h1>Error 400</h1>\n\
    <p>Your request was badly formatted. Can you be more careful?</p>\n\
  </body>\n\
</html>\n"  

#define SERVER_FAILURE_REPLY "%s 500 Server Failure\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Error 500 - Server Failure</title></head>\n\
  <body><h1>Error 500</h1>\n\
    <p>Duuuuude, the server couldn't do it!</p>\n\
  </body>\n\
</html>\n"  

/* Parameters: protocol */
#define FORBIDDEN_REPLY "%s 403 Forbidden\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head>\n\
    <title>Error 403 - Forbidden</title>\n\
  </head>\n\
  <body>\n\
    <h1>Error 403</h1>\n\
    <p>Request forbidden, smartass!</p>\n\
  </body>\n\
</html>\n"  
 
/* Parameters: protocol, content type */
#define HEADER_REPLY "%s 200 OK\r\n\
Content-Type: %s\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n"

/* Parameters: protocol */
#define FILE_SAVED_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>File Saved</title></head>\n\
  <body><h1>File Saved</h1>\n\
     <p>Your file has been saved.</p>\n\
  </body>\n\
</html>\n"

/* Parameters: protocol */
#define QUERY_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Query: not implemented</title></head>\n\
  <body><h1>Query functionality not implemented</h1>\n\
     <p>We want to save something for version 2.0.</p>\n\
  </body>\n\
</html>\n"


/* Parameter: protocol */
#define RESOURCE_NOT_FOUND_REPLY "%s 404 File Not Found\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Error 404 - Resource Not Found</title></head>\n\
  <body><h1>Error 404</h1>\n\
     <p>Where is it? Where is it? I saw it here a moment ago...</p>\n\
  </body>\n\
</html>\n"

/* Parameter: protocol */
#define BAD_LOGIN_REPLY "%s 403 Forbidden\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Error 403 - Forbidden</title></head>\n\
  <body><h1>Error 403</h1>\n\
     <p>Loser! Your login process failed miserably.</p>\n\
     <p>The reason? Simply put: %s</p>\n\
  </body>\n\
</html>\n"

/* Parameter: protocol */
#define MISSING_AUTH_REPLY "%s 403 Forbidden\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Error 403 - Forbidden</title></head>\n\
  <body><h1>Error 403</h1>\n\
     <p>Hey! I told you to authenticate through the biometric system first!</p>\n\
     <p>What are you trying to do?</p>\n\
  </body>\n\
</html>\n"

/* Parameter: protocol, new URL, new URL, new URL */
#define RESOURCE_ELSEWHERE_REPLY "%s 303 See Other\r\n\
Content-Type: text/html\r\n\
Location: %s\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>Redirect</title></head>\n\
  <body><h1>Redirect</h1>\n\
     <p>The requested resource can be accessed elsewhere, for example at <a href=\"%s\">%s</a></p>\n\
  </body>\n\
</html>\n"

/* Error codes */
#define ERR_WRONG_PARAMS 1
#define ERR_LOGGING 2
#define ERR_DAEMON 3
#define ERR_CONF 4
#define ERR_MEMORY 5
#define ERR_SOCK_CREATE 6
#define ERR_SOCK_SELECT 7
#define ERR_FORK 8
#define ERR_SSL_INIT 9
#define ERR_SSL_WRITE 10
#define ERR_SSL_READ 11
#define ERR_SOCK_ACCEPT 12

/*
 * DATA STRUCTURES
 */
struct peer {
  char* hostname;
  char* port;
  /* struct sockaddr_in addr; */

  struct peer *prev;
  struct peer *next;
};

struct http_request {
  char *method;
  char *resource;
  char *protocol;
  char *header;
  char *type;
  /* char *body; */
};

/*
 * GLOBALS
 */
int debug = 0;

/*
 * FUNCTIONS
 */
void 
reaper(int sig)
{
  int status;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "SIGCHLD handler: start\n");
#endif

  while (waitpid(-1, &status, WNOHANG) > 0);

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, 
	   "SIGCHLD handler: child exited with status %d\n", status);
#endif

  return;
}

/* Puts the contents of a file into memory 
   Returns a malloc'ed buffer that has to be freed with free */
char *
file_to_buf(FILE *f)
{
  int filesize = 0;
  int ret = 0;
  char *buf = NULL;

  assert(f);

  if (fseek(f, 0, SEEK_END) < 0)
    {
      my_error(__FILE__, __LINE__, "cannot seek file");
      return NULL;
    }
    
  filesize = ftell(f);

  if (filesize < 0)
    {
      my_error(__FILE__, __LINE__, "cannot determine the size of file");
      return NULL;
    }

  buf = (char *)malloc(filesize + 1);
  if (buf == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory to hold file");
      return NULL;
    }

  fseek(f, 0, SEEK_SET);
  ret = fread(buf, 1, filesize, f);

  if (ret < filesize)
    {
      my_error(__FILE__, __LINE__, 
	       "read failed and returned %d when reading file of size %d", 
	       ret, filesize);
      free(buf);
      return NULL;
    }

  buf[filesize] = '\0';

  return buf;
}

int 
parse_peers(struct peer *peers, char *buf)
{
  int peerstart = 0;
  int peerend = 0;
  int portstart = 0;
  int portend = 0;
  int i = 0, j = 0;
  int len = 0;
  struct peer *new_peer = NULL;

  assert(peers);
  assert(buf);

  len = strlen(buf);

#define CHECK(i) if (i >= len) goto end;
  
  i = 0;
  while(1)
    {
      while (isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      if (buf[i] == '#')
	{
	  while (buf[i] != '\n')
	    {
	      i++ ;
	      CHECK(i);
	    }
	  continue;
	}
      peerstart = i;
      while (!isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      peerend = i; 
      while (isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      portstart =i;
      while (!isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      portend = i; 
      
      new_peer = malloc(sizeof(struct peer));
      if (new_peer == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  return ERR_MEMORY;
	}
      new_peer->hostname = malloc((peerend - peerstart) + 1);
      if (new_peer->hostname == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  return ERR_MEMORY;
	}

      for (j = peerstart; j < peerend; j++)
	{
	  new_peer->hostname[j - peerstart] = buf[j];
	}
      new_peer->hostname[j - peerstart] = '\0';
	
      new_peer->port = malloc((portend - portstart) + 1);
      if (new_peer->port == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  return ERR_MEMORY;
	}
      for (j = portstart; j < portend; j++)
	{
	  new_peer->port[j - portstart] = buf[j];
	}
      new_peer->port[j - portstart] = '\0';

      new_peer->prev = peers->prev;
      peers->prev->next = new_peer;
      peers->prev = new_peer;
      new_peer->next = peers;
      
      if (debug) my_debug(__FILE__, __LINE__, 
			  "created peer \"%s\" with port \"%s\"", 
			  new_peer->hostname, new_peer->port);
    }
  
 end:
  return 0;
}

/* Request parsing routine: malloc()'s both the request
   structure and the request fields (see free_request()) */ 
struct http_request* 
parse_request(char *data)
{
  char *buf = NULL;
  char *method = NULL;
  char *resource = NULL;
  char *protocol = NULL;
  char *protoend = NULL;
  char *header = NULL;
  char *type = NULL;
  char *extension = NULL;
  struct http_request *request = NULL;
  int j;

  assert(data);

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "parsing request (%d bytes) [%s]", 
	   strlen(data), data);
#endif

  /* Creates "safe" modifiable copy */
  buf = strdup(data);
  if (buf == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }

  /* Parses the request */
  method = buf;
  resource = strchr(method, ' ');
  if (resource == NULL)
    {
      my_error(__FILE__, __LINE__, "wrong request format");
      free(buf);
      return NULL;
    }
  resource[0] = '\0';

  resource++;
  protocol = strchr(resource, ' ');

  if (protocol == NULL)
    {
      my_error(__FILE__, __LINE__, "wrong request format");
      free(buf);
      return NULL;
    }
  protocol[0] = '\0';
  protocol++;

  protoend = strchr(protocol, '\r');
  if (protoend == NULL)
    {
      my_error(__FILE__, __LINE__, "wrong request format");
      free(buf);
      return NULL;
    }
  protoend[0] = '\0';
  header = protoend + 2;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, 
	   "method: [%s], url: [%s], protocol [%s]", 
	   method, resource, protocol);
#endif

  extension = NULL;
  for (j = strlen(resource) - 1; j >= 0; j--)
    {
      if (resource[j] == '.') 
	{
	  extension = &(resource[j + 1]);
	  break;
	}
    }
  if (extension == NULL)
    {
      type = "application/octet-stream";
    }
  else if ((!strcasecmp(extension, "html")) || (!strcasecmp(extension, "htm")))
    {
      type = "text/html";
    }
  else if ((!strcasecmp(extension, "jpeg")) || (!strcasecmp(extension, "jpg")))
    {
      type = "image/jpeg";
    }
  else if (!strcasecmp(extension, "gif"))
    {
      type = "image/gif";
    }
  else if (!strcasecmp(extension, "png"))
    {
      type = "image/png";
    }
  else if (!strcasecmp(extension, "txt"))
    {
      type = "text/plain";
    }
  else if (!strcasecmp(extension, "css"))
    {
      type = "text/css";
    }
  else
    {
      type = "application/octet-stream";
    }
  request = (struct http_request *)malloc(sizeof(struct http_request));

  if (request == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      free(buf);
      return NULL;
    }

  request->method = strdup(method);
  request->resource = strdup(resource);
  request->protocol = strdup(protocol);
  request->header = strdup(header);
  request->type = strdup(type);
  
  free(buf);
  return request;
}

void free_request(struct http_request *r)
{
  if (r == NULL) return;
  if (r->method != NULL) free(r->method);
  if (r->resource != NULL) free(r->resource);
  if (r->protocol != NULL) free(r->protocol);
  if (r->header != NULL) free(r->header);
  if (r->type != NULL) free(r->type);
  
  free(r);
  return;
}  

     
char *
request_to_str(struct http_request *r)
{
  char *str = NULL;
  int size = 0;

  assert(r);

#define REQ_FORMAT "\
Method   [%s]\n\
Resource [%s]\n\
Protocol [%s]\n\
Header:\n\
%s"
  
  size = strlen(r->method) + strlen(r->resource) + strlen(r->protocol) +
    strlen(r->header) + strlen(REQ_FORMAT) + 1;
  
  str = malloc(size);
  if (str == NULL) 
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }
  sprintf(str, REQ_FORMAT, 
	  r->method, r->resource, r->protocol, r->header);
  
  return str;
}

#define MAXNUMSTRING 256
int 
get_body_size(struct http_request *r)
{
  char *content = NULL;
  char buf[MAXNUMSTRING];
  int i = 0;

  assert(r);
  assert(r->header);

  content = strstr(r->header, "\r\nContent-Length:");
  if (content == NULL)
    {
#ifdef DEBUG
      my_error(__FILE__, __LINE__, "can't find Content-Length field in %s", r->header);
#endif
      return -1;
    }
  content += strlen("\r\nContent-Length:");
  while (isspace(content[0])) content ++;
  i = 0;
  while(isdigit(content[i]))
    {
      buf[i] = content[i];
      i++;
      if (i == MAXNUMSTRING) return -1;
    }
  buf[i] = '\0';
  return atoi(buf);
}

struct http_request*
parse_ssl_request(SSL *ssl)
{
  struct http_request *r = NULL;
  char data[BUFSIZE];
  int index = 0;
  char c = '\0';
  int ret = 0;

  assert(ssl);

  while (1)
    {
      ret = SSL_read(ssl, &c, 1);
      /* EOF */
      if (ret == 0)
	{
	  break;
	}
      /* ERROR */
      if (ret < 0)
	{
	  return NULL;
	}
      data[index] = c;
      index++;
      data[index] = '\0';

      if (!strcmp(&(data[index - 4]), "\r\n\r\n"))
	{
	  break;
	}
    }

  r = parse_request(data);
  return r;
}

int
check_resource(char *resource)
{
  assert(resource);

  /* Checks that this is an absolute path */
  if (resource[0] != '/') return -1;

  /* Checks that this is not a directory */
  if (opendir(resource) != NULL) return -1;

  return 0;
}

char * 
ask_peers(char *resource, struct peer *peers, int timeout)
{
  struct peer *peer;
  int udp_sd;
  struct sockaddr_in peer_addr; /* an Internet endpoint address */
  int peer_addr_len; /* an Internet endpoint address */
  char reply[MAX_QUERY_SIZE];
  fd_set connections;
  struct timeval time;
  struct hostent *phe;
  int ret;
  char *url_ptr = NULL;

  assert(resource);
  assert(peers);

  /* No peers */
  if (peers->next == peers) 
    {
      if (debug) my_debug(__FILE__, __LINE__, "no peers to query");
      return NULL;
    }

  time.tv_sec = timeout;
  time.tv_usec = 0;

  /* Creates a UDP socket (unconnected) */
  if ((udp_sd = unconnectedUDP()) < 0)
    return NULL;
  
  for (peer = peers->next; peer != peers; peer = peer->next)
    {
      if (debug) my_debug(__FILE__, __LINE__, "asking peer %s:%s", peer->hostname, peer->port);
      memset(&peer_addr, 0, sizeof(peer_addr));
      peer_addr_len = sizeof(peer_addr);
      peer_addr.sin_family = AF_INET;
      peer_addr.sin_port = (int)strtol(peer->port, (char **)NULL, 10);
      if (peer_addr.sin_port == 0) 
	{
	  my_error(__FILE__, __LINE__, "failed to undertand peer %s port \"%s\"",
		   peer->hostname, peer->port);
	  return NULL;
	}

      /* Map host name to IP address, allowing for dotted decimal */
      if ((phe = gethostbyname(peer->hostname)))
	{
	  memcpy(&peer_addr.sin_addr, phe->h_addr, phe->h_length);
	}
      else if ((peer_addr.sin_addr.s_addr = inet_addr(peer->hostname)) == INADDR_NONE)
	{
	  my_error(__FILE__, __LINE__, "can't resolve peer name \"%s\"", peer->hostname);
	  return NULL;
	}

      if (sendto(udp_sd, 
		 resource, 
		 strlen(resource), 
		 0, 
		 (struct sockaddr *)&peer_addr, 
		 sizeof(peer_addr)) < 0)
	{
	  my_error(__FILE__, __LINE__, "can't send query to peer \"%s\"", peer->hostname);
	  continue;
	}
    }

  while (1)
    {
      FD_ZERO(&connections);
      FD_SET(udp_sd, &connections);
      
      ret = select(udp_sd + 1, &connections, NULL, NULL, &time);
      
      if (ret < 0)
	{
	  if (errno == EINTR)
	    {
	      continue;
	    }
	  else
	    {
	      my_error(__FILE__, __LINE__, "select() on query socket failed");
	      exit(ERR_SOCK_SELECT);
	    }
	}
      /* No answer received */
      else if (ret == 0) 
	{
	  if (debug) my_debug(__FILE__, __LINE__, "timeout expired, giving up");
	  return NULL;
	}
      /* Error */
      else if (!FD_ISSET(udp_sd, &connections))
	{
	  my_error(__FILE__, __LINE__, "select() on query socket returned no socket");
	  return NULL;
	}
      else
	{

	  /* Parse reply */
	  memset(&peer_addr, 0, sizeof(peer_addr));
	  peer_addr_len = sizeof(peer_addr);
	  ret = recvfrom(udp_sd, reply, MAX_QUERY_SIZE, 0, 
			 (struct sockaddr *)&peer_addr, &peer_addr_len);
	  reply[ret] = '\0';
	  if (strlen(reply) == 0)
	    {
	      if (debug) my_debug(__FILE__, __LINE__, "received empty reply");
	      continue;
	    }
	  
	  if (debug) my_debug(__FILE__, __LINE__, "received reply [%s]", reply);

	  if ((url_ptr = strchr(reply, '\n')) == NULL)
	    {
	      my_error(__FILE__, __LINE__, "received malformed reply %s", reply);
	      return NULL;
	    }
	  *url_ptr = '\0';

	  if (debug) my_debug(__FILE__, __LINE__, "redirecting client to %s", reply);
	  url_ptr = strdup(reply);

	  return url_ptr;
	}
    }

  /* Never reached */
  return NULL;

}

int process_login(struct http_request *r, SSL* ssl) 
{
  char command[512];
  char reply[2048] = {0};
  char msg[1024];
  char *request = NULL;
  char *p = NULL;
  char *user = NULL;
  char *password = NULL;
  char *operation = NULL;
  FILE *f = NULL;
  char commout[512] = {0};
  int ret;

  request = r->resource;

  if (debug) 
    {
      my_debug(__FILE__, __LINE__, "Parsing login: %s", request);
    }

  /* Request is in the format: /login?user=<username>&password=<password>&operation=<operation>*/
  p = memchr(request, '?', strlen(request));

  if (p == NULL)
    {
      sprintf(msg, "Missing parameters in login request: %s\n", request);
      goto end;
    }
  user = p + strlen("user=") + 1;
  p = memchr(user, '&', strlen(user));
  if (p == NULL)
    {
      sprintf(msg, "Missing user in login request: %s\n", request);
      goto end;
    }
  *p = '\0';
  password = p + strlen("password=") + 1;
  p = memchr(password, '&', strlen(password));
  if (p == NULL)
    {
      sprintf(msg, "Missing password in login request: %s\n", request);
      goto end;
    }
  *p = '\0';
  operation = p + strlen("operation=") + 1;

  sprintf(command, "./biometric %s %s %s", user, password, operation);
  if (debug) my_debug(__FILE__, __LINE__, "executing %s", command);

  f = popen(command, "r");
  if (f == NULL)
    {
      my_error(__FILE__, __LINE__, "can't popen command");
      sprintf(reply, SERVER_FAILURE_REPLY, r->protocol);
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	}
      return ERR_FORK;
    } 

  sprintf(reply, HEADER_REPLY, r->protocol, "text/html");
  ret = SSL_write(ssl, reply, strlen(reply));
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't write to SSL connection");
      ret = ERR_SSL_WRITE;
    }

  while (1)
    {
      ret = fread(commout, 512, 1, f);
      if (ret <= 0) break;
    }
  ret = SSL_write(ssl, commout, strlen(commout));

  return 0;
 end:
  sprintf(reply, BAD_LOGIN_REPLY, r->protocol, msg);
  ret = SSL_write(ssl, reply, strlen(reply));
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't write to SSL connection");
      ret = ERR_SSL_WRITE;
    }

  return 0;
}

int 
process_store(struct http_request *r, SSL *ssl)
{
  char reply[2048] = {0};
  char msg[1024];
  char *request = NULL;
  char *p = NULL;
  char *user = NULL;
  char *filename = NULL;
  char *content = NULL;
  FILE *f = NULL;
  int ret;
  struct stat stat_data;

  request = r->resource;

  if (debug) 
    {
      my_debug(__FILE__, __LINE__, "Parsing store: %s", request);
    }

  /* Request is in the format: /store?filename=<file>&content=<content>&user=<username>*/
  p = memchr(request, '?', strlen(request));

  if (p == NULL)
    {
      sprintf(msg, "Missing parameters in store request: %s\n", request);
      goto end;
    }
  filename = p + strlen("filename=") + 1;
  p = memchr(filename, '&', strlen(filename));
  if (p == NULL)
    {
      sprintf(msg, "Missing filename in store request: %s\n", request);
      goto end;
    }
  *p = '\0';
  content = p + strlen("content=") + 1;
  p = memchr(content, '&', strlen(content));
  if (p == NULL)
    {
      sprintf(msg, "Missing content in store request: %s\n", request);
      goto end;
    }
  *p = '\0';
  user = p + strlen("user=") + 1;

  /* Checks if user has authenticated */
  if (stat(user, &stat_data) != 0)
    {
      sprintf(reply, MISSING_AUTH_REPLY, r->protocol);
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	}
      return 0;
    }
  f = fopen(filename, "w");

  if (f == NULL)
    {
      my_error(__FILE__, __LINE__, "can't open file to store content");
      sprintf(reply, SERVER_FAILURE_REPLY, r->protocol);
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	}
      return ERR_FORK;
    } 

  fwrite(content, strlen(content), 1, f);
  fclose(f);

  sprintf(reply, FILE_SAVED_REPLY, r->protocol);
  ret = SSL_write(ssl, reply, strlen(reply));
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't write to SSL connection");
      ret = ERR_SSL_WRITE;
    }
  
  return 0;
 end:
  sprintf(reply, BAD_LOGIN_REPLY, r->protocol, msg);
  ret = SSL_write(ssl, reply, strlen(reply));
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't write to SSL connection");
      ret = ERR_SSL_WRITE;
    }

  return 0;
}

int 
process_https_query(struct http_request *r, SSL *ssl)
{
  char reply[2048] = {0};
  int ret;

  sprintf(reply, QUERY_REPLY, r->protocol);
  ret = SSL_write(ssl, reply, strlen(reply));
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't write to SSL connection");
      ret = ERR_SSL_WRITE;
    }
  
  return 0;
} 

int 
process_https(struct peer *peers, int https, SSL_CTX* ctx, struct sockaddr_in *client, int timeout)
{
  char reply[REPLYSIZE] = {0};
  struct http_request *r = NULL;
  int ret = 0; /* Return value */
  char *str = NULL;
  char buf[BUFSIZE] = {0};
  struct stat stat_data;
  FILE *rfile = NULL;
  char *new_url = NULL;
  char *rfilename = NULL;
  SSL* ssl = NULL;
  int i = 0;

  assert(peers);
  assert(client);
  assert(ctx);

  /* Creates new SSL connection from context */
  ssl = SSL_new(ctx);
  if (ssl == NULL)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "could not create SSL connection");
      ret = ERR_SSL_INIT;
      goto end;
    }

  /* Sets the file descriptor for the SSL connection */ 
  SSL_set_fd(ssl, https);

  /* Accepts the connection */
  ret = SSL_accept(ssl);
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, 
	       "could not accept SSL connection");
      ret = ERR_SSL_INIT;
      goto end;
    }

  if (debug) my_debug(__FILE__, __LINE__, "SSL connection using %s\n", 
		      SSL_get_cipher(ssl));
  
  /* Parses the request (r is malloc()ed and needs to be
     free()ed with free_request()) */
  r = parse_ssl_request(ssl);
  if (r == NULL)
    {
      sprintf(reply, BAD_REQUEST_REPLY, "HTTP/1.1");
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	}
      goto end;
    }
  if (debug)
    {
      str = request_to_str(r);
      my_debug(__FILE__, __LINE__, "received request\n%s\n", str);
      free(str);
    }

  /* Maps '/' to '/index.html' */
  if (!strcmp(r->resource, "/"))
    {
      free(r->resource);
      r->resource = strdup("/index.html");
      free(r->type);
      r->type = strdup("text/html");
    }

  /* Resource is forbidden  */
  if (check_resource(r->resource))
    {
      sprintf(reply, BAD_REQUEST_REPLY, r->protocol);
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	}
      goto end;
    }

  /* Login procedure */
  if (!strncmp(r->resource, "/login", strlen("/login")))
    {
      if (debug)
	{
	  my_debug(__FILE__, __LINE__, "Login resource %s\n", r->resource);
	}
      process_login(r, ssl);
      goto end;
  }

  /* Storage procedure */
  if (!strncmp(r->resource, "/store", strlen("/store")))
    {
      if (debug)
	{
	  my_debug(__FILE__, __LINE__, "Storing resource %s\n", r->resource);
	}
      process_store(r, ssl);
      goto end;
  }

  /* Storage procedure */
  if (!strncmp(r->resource, "/query", strlen("/query")))
    {
      if (debug)
	{
	  my_debug(__FILE__, __LINE__, "Querying resource %s\n", r->resource);
	}
      process_https_query(r, ssl);
      goto end;
  }
      
  
  /* Skips initial '/' */
  i = 0;
  while (r->resource[i] == '/') 
    {
      i++;
    }
  rfilename = &(r->resource[i]);
  
  /* Resource is available */
  if (stat(rfilename, &stat_data) == 0)
    {
      /* If it's a directory or cannot be opened */
      if ((stat_data.st_mode & S_IFDIR) || 
	  ((rfile = fopen(rfilename, "r")) == NULL))
	{
	  sprintf(reply, FORBIDDEN_REPLY, r->protocol);
	  ret = SSL_write(ssl, reply, strlen(reply));
	  if (ret < 0)
	    {
	      ERR_print_errors_fp(stderr);
	      my_error(__FILE__, __LINE__, "can't write to SSL connection");
	      ret = ERR_SSL_WRITE;
	    }
	  goto end;
	}    

      if (debug) my_debug(__FILE__, __LINE__, "sending filename %s", rfilename);

      /* Sends the reply header */
      sprintf(reply, HEADER_REPLY, r->protocol, r->type);
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	  goto end;
	}
      if (debug) my_debug(__FILE__, __LINE__, "sending header: [%s]\n", reply);

      
      /* Sends the reply body */
      while (1)
	{
	  if ((ret = fread(buf, 1, BUFSIZE, rfile)) != 0)
	    {
	      ret = SSL_write(ssl, buf, ret);
	      if (ret < 0)
		{
		  ERR_print_errors_fp(stderr);
		  my_error(__FILE__, __LINE__, "can't write to SSL connection");
		  ret = ERR_SSL_WRITE;
		  goto end;
		}
	      if (ret < BUFSIZE) break;
	    }
	  else
	    {
	      break;
	    }
	}
      goto end;
    }
  /* Resource not available, ask peers */
  else
    {
      if ((new_url = ask_peers(r->resource, peers, timeout)) == NULL)
	{
	  sprintf(reply, RESOURCE_NOT_FOUND_REPLY, r->protocol);
	  ret = SSL_write(ssl, reply, strlen(reply));
	  if (ret < 0)
	    {
	      ERR_print_errors_fp(stderr);
	      my_error(__FILE__, __LINE__, "can't write to SSL connection");
	      ret = ERR_SSL_WRITE;
	    }
	  goto end;
	}
      sprintf(reply, RESOURCE_ELSEWHERE_REPLY, 
	      r->protocol, new_url, new_url, new_url);
      ret = SSL_write(ssl, reply, strlen(reply));
      if (ret < 0)
	{
	  ERR_print_errors_fp(stderr);
	  my_error(__FILE__, __LINE__, "can't write to SSL connection");
	  ret = ERR_SSL_WRITE;
	}
      goto end;
    }
 end:
  if (r) free_request(r);
  if (new_url) free(new_url);
  if (ssl) SSL_free(ssl); 
  close(https);

  return ret;
}

int 
process_query(char* hostname, char* ssl_port, char *query_buf, 
	      int udp_sd, struct sockaddr_in *client)
{
  char reply[MAX_QUERY_SIZE] = {0};
  struct stat stat_data;
  char *filename = NULL;
  int i;
  char *p = NULL;
  FILE *f = NULL;

  assert(hostname);
  assert(ssl_port);
  assert(query_buf);
  assert(client);

  /* Resource is available */
  i = 0;
  while (query_buf[i] == '/')
    {
      i++;
    }
  filename = &(query_buf[i]);

  /* Remove ending newline */
  p = filename + strlen(filename) - 1;
  while (isspace(*p))
    {
      *p = '\0';
      p--;
    }
  
  sprintf(reply, "https://%s:%s/%s\n-", hostname, ssl_port, filename);
  
  if (stat(filename, &stat_data) != 0)
    {
      if (debug) my_error(__FILE__, __LINE__, "file %s not found, stay silent", query_buf);
      return -1;
    }
  
  if ((f = fopen(filename, "r")) != NULL)
    {
      p = file_to_buf(f);
      if (p != NULL)
	{
	  if (strlen(p) < 128)
	    {
	      reply[strlen(reply) - 1] = '+';
	      strcat(reply, p);
	    }
	}
      free(p);
    }

  if ((sendto(udp_sd, reply, strlen(reply), 0, 
	      (struct sockaddr *)client, 
	      sizeof(struct sockaddr_in))) < 0) 
    {
      my_error(__FILE__, __LINE__, "cannot send reply %s to host %s:%d", 
	       reply, inet_ntoa(client->sin_addr), ntohs(client->sin_port));
      return -1;
    }

  if (debug) my_debug(__FILE__, __LINE__, "reply [%s] sent to peer %s:%d",
		      reply, 
		      inet_ntoa(client->sin_addr), 
		      ntohs(client->sin_port));
  return 0;
}

int 
main(int argc, char *argv[])
{
  struct peer peers;
  char *ssl_port = DEFAULT_SSL_PORT;
  char *udp_port = DEFAULT_UDP_PORT;
  char *doc_dir = DEFAULT_DOCDIR;
  char *conf_filename = NULL;
  FILE *conf_file = NULL;
  char *conf_buf = NULL;
  int daemon = 0;
  char *log_filename = NULL;
  char hostname[MAXHOSTNAMELEN];
  int https = 0;
  int query = 0;
  int max_socket = 0;
  fd_set connections;
  int new_https = 0;
  struct sockaddr_in client_addr;
  int client_addr_len = 0;
  char query_buf[MAX_QUERY_SIZE];
  int request_type = 0;
  int pid = 0;
  int ret = 0;
  int i;
  int timeout = DEFAULT_TIMEOUT;
  SSL_CTX* ctx = NULL;
  SSL_METHOD *meth = NULL;
  int accept_counter = 0;
  int fd;

  /* Initializes peer list pointers */
  peers.next = &peers;
  peers.prev = &peers;

  /* Initializes the SSL library */
  SSL_load_error_strings();
  SSL_library_init();

  /* Creates SSL server context */
  if ((meth = SSLv23_server_method()) == NULL)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't set SSL server method");
      exit(ERR_SSL_INIT);
    }
  ctx = SSL_CTX_new(meth);
  if (!ctx) 
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't initialize the SSL context");
      exit(ERR_SSL_INIT);
    }

  /* Sets certificate */
  if (SSL_CTX_use_certificate_file(ctx, 
				   DEFAULT_CERT_FILE, 
				   SSL_FILETYPE_PEM) <= 0) 
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "server certificate not found");
      exit(ERR_SSL_INIT);
    }

  /* Sets private key */
  if (SSL_CTX_use_PrivateKey_file(ctx, 
				  DEFAULT_KEY_FILE, 
				  SSL_FILETYPE_PEM) <= 0) 
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "private key not found");
      exit(ERR_SSL_INIT);
    }
  if (!SSL_CTX_check_private_key(ctx)) 
    {
      my_error(__FILE__, __LINE__, 
	       "private key does not match the certificate's public key");
      exit(ERR_SSL_INIT);
    }


  /* Sets the SIGCHILD handler */
  signal(SIGCHLD, reaper);

  /* Parses the command line arguments */
  hostname[0] = '\0';
  i = 1;
  while (i < argc)
    {
      if (!strcmp(argv[i], "--port"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  ssl_port = argv[i];
	}
      else if (!strcmp(argv[i], "--docs"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  doc_dir = argv[i];
	}
      else if (!strcmp(argv[i], "--query"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  udp_port = argv[i];
	}
      else if (!strcmp(argv[i], "--conf"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  conf_filename = argv[i];
	}
      else if (!strcmp(argv[i], "--timeout"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  timeout = (int)strtol(argv[i], (char **)NULL, 10);
	  if (timeout <= 0)
	    {
	      my_error(__FILE__, __LINE__, "null or negative timeout: %s", argv[i]);
	      exit(ERR_WRONG_PARAMS);
	    }
	}
      else if (!strcmp(argv[i], "--servername"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  strncpy(hostname, argv[i], MAXHOSTNAMELEN - -1);
	}
      else if (!strcmp(argv[i], "--daemon"))
	{
	  daemon = 1;
	}
      else if (!strcmp(argv[i], "--nodaemon"))
	{
	  daemon = 0;
	}
      else if (!strcmp(argv[i], "--debug"))
	{
	  debug = 1;
	}
      else if (!strcmp(argv[i], "--logfile"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  log_filename = argv[i];
	}
      else
	{
	  my_error(__FILE__, __LINE__, 
		    "unknown parameter %s", argv[i]);
	  exit(ERR_WRONG_PARAMS);
	}
      i++;
    }

  /* Hostname has not been specified */
  if (strlen(hostname) == 0)
    {
      my_error(__FILE__, __LINE__, 
	       "You need to specify a host name (or IP address) using the --servername option");
      exit(ERR_WRONG_PARAMS);
    }

  if (debug) my_debug(__FILE__, __LINE__, "using hostname: [%s]", hostname);

  /* Determines daemon behavior */
  if (daemon)
    {
      /* Goes in the background */
      pid = fork();
      if (pid < 0)  
	{
	  my_error(__FILE__, __LINE__, "can't go in the background");
	  exit(ERR_DAEMON);
	}
      if (pid > 0) exit(0);

      
      /* Creates a new group and detaches from the controlling terminal */
      if (setsid() < 0)
	{
	  my_error(__FILE__, __LINE__, "can't create new process group");
	  exit(ERR_DAEMON);
	}

      /* Kills the parent process, so that the controlling terminal cannot be
	 rgained */
      pid = fork();
      if (pid < 0)  
	{
	  my_error(__FILE__, __LINE__, "can't fork new process in new process group");
	  exit(ERR_DAEMON);
	}
      if (pid > 0) exit(0);

      /* Redirects stdin, stdout, and stderr to log file (or /dev/null) */
      if (log_filename == NULL)
	{
	  log_filename = "/dev/null";
	}
      if ((fd = open(log_filename, O_RDONLY | O_CREAT, 666)) < 0)
	{
	  my_error(__FILE__, __LINE__, "can't open log file %s", log_filename);
	  exit(ERR_DAEMON);
	}
      if (dup2(fd, 0) < 0)
	{
	  my_error(__FILE__, __LINE__, "can't redirect stdin to %s", log_filename);
	  exit(ERR_DAEMON);
	}
      if (dup2(fd, 1) < 0)
	{
	  my_error(__FILE__, __LINE__, "can't redirect stdout to %s", log_filename);
	  exit(ERR_DAEMON);
	}
      if (dup2(fd, 2) < 0)
	{
	  my_error(__FILE__, __LINE__, "can't redirect stderr to %s", log_filename);
	  exit(ERR_DAEMON);
	}
      if (fd > 2) close(fd);
    }
  else
    {
      /* Determines the file to log to */
      if (log_filename != NULL)
	{
	  if ((fd = open(log_filename, O_RDONLY | O_CREAT, 666)) < 0)
	    {
	      my_error(__FILE__, __LINE__, "can't open log file %s", log_filename);
	      exit(ERR_LOGGING);
	    }
	  if (dup2(fd, 2) < 0)
	    {
	      my_error(__FILE__, __LINE__, "can't redirect stderr to %s", log_filename);
	      exit(ERR_DAEMON);
	    }
	  close(fd);
	}
    }

  /* Parses the configuration file */
  if (conf_filename == NULL)
    {
      /* No filename specified: open the default configuration file */
      if (debug) my_debug(__FILE__, __LINE__, "using default config filename: %s", DEFAULT_CONFFILE);
      conf_file = fopen(DEFAULT_CONFFILE, "r");
    }
  else 
    {
      if (debug) my_debug(__FILE__, __LINE__, "using config filename: %s", conf_filename);

      /* A filename has been specified: the filename must exist */
      if ((conf_file = fopen(conf_filename, "r")) == NULL)
      my_error(__FILE__, __LINE__, "cannot open conf file \"%s\"", conf_filename);
      exit(ERR_CONF);
    }
  /* If a conf file exists, parses it */
  if (conf_file != NULL)
    {
      if ((conf_buf = file_to_buf(conf_file)) == NULL)
	{
	  my_error(__FILE__, __LINE__, 
		   "cannot read configuration file \"%s\"", conf_filename);
	  exit(ERR_CONF);
	}
      if (debug) my_debug(__FILE__, __LINE__, "parsing peer file: %s", conf_buf);
      if (parse_peers(&peers, conf_buf))
	{
	  my_error(__FILE__, __LINE__, 
		   "cannot parse configuration file \"%s\"", conf_filename);
	  exit(ERR_CONF);
	}	  
      free(conf_buf);
    }

  /* Sets the document directory */
  if (chdir(doc_dir) < 0)
    {
      my_error(__FILE__, __LINE__, "cannot change to doc dir \"%s\"", doc_dir);
      exit(ERR_CONF);
    }
  if (debug) my_debug(__FILE__, __LINE__, "using document dir: [%s]", doc_dir);

  /* Creates passive SSL socket */
  if ((https = passiveTCP(ssl_port)) < 0)
    {
      my_error(__FILE__, __LINE__, 
	    "can't create server SSL/TCP socket on port %s", ssl_port);
      exit(ERR_SOCK_CREATE);
    }

  /* Creates passive UDP socket */
  if ((query = passiveUDP(udp_port)) < 0)
    {
      my_error(__FILE__, __LINE__, 
	    "can't create server UDP socket on port %s", udp_port);
      exit(ERR_SOCK_CREATE);
    }

  if (debug) my_debug(__FILE__, __LINE__, 
		      "waiting for https requests on port %s and for queries on port %s", 
		      ssl_port, udp_port);

  /* Waits for a connection on either socket */
  max_socket = 0;
  if (max_socket <= https) 
    max_socket = https + 1;
  if (max_socket <= query)
    max_socket = query + 1;
  accept_counter = 0;
  while (1)
    {
      FD_ZERO(&connections);
      FD_SET(https, &connections);
      FD_SET(query, &connections);
      
      ret = select(max_socket, &connections, NULL, NULL, NULL);
      
      if (ret < 0)
	{
	  if (errno == EINTR)
	    {
	      continue;
	    }
	  else
	    {
	      my_error(__FILE__, __LINE__, "select() on https/query sockets failed");
	      exit(ERR_SOCK_SELECT);
	    }
	}

      new_https = -1;
      memset(&client_addr, 0, sizeof(client_addr));
      client_addr_len = sizeof(client_addr);

      if (FD_ISSET(https, &connections))
	{
	  new_https = accept(https, 
			     (struct sockaddr *)&client_addr, 
			     &client_addr_len);
	  if (new_https < 0)
	    {
	      my_error(__FILE__, __LINE__, 
		       "accept() on https socket %d failed", https);
	      if (accept_counter++ > ACCEPT_FAILURE_THRESHOLD)
		{
		  exit(ERR_SOCK_ACCEPT);
		}
	      continue; /* Try all over again */
	    }
	  request_type = REQUEST_HTTPS;
	  if (debug) my_debug(__FILE__, __LINE__, "received connection request from %s", 
			      inet_ntoa(client_addr.sin_addr));
	}
      else if (FD_ISSET(query, &connections))
	{
	  ret = recvfrom(query, query_buf, MAX_QUERY_SIZE, 0,
			 (struct sockaddr *)&client_addr, 
			 &client_addr_len);
	  if (ret < 0)
	    {
	      my_error(__FILE__, __LINE__, "failed to read peer's query");
	      continue; /* Try all over again */
	    }
	  query_buf[ret] = '\0';
	  request_type = REQUEST_QUERY;
	  if (debug) my_debug(__FILE__, __LINE__, "received query from host %s:%d [%s]", 
			      inet_ntoa(client_addr.sin_addr), 
			      ntohs(client_addr.sin_port),
			      query_buf);
	}
      else
	{
	  my_error(__FILE__, __LINE__, "select() did not return any active socket");
	  close(https);
	  close(query);
	  exit(ERR_SOCK_SELECT);
	}

#ifndef ITERATIVE      
      /* Forks a new process to serve this client */ 
      pid = fork();

      if (pid < 0)
	{
	  my_error(__FILE__, __LINE__, "fork() failed");
	  exit(ERR_FORK);
	}

      /* Beginning of child code */
      if (pid == 0)
	{
	  close(https);
#endif
	  if (request_type == REQUEST_HTTPS)
	    {
	      ret = process_https(&peers, new_https, ctx, &client_addr, timeout);
	    }
	  else if (request_type == REQUEST_QUERY)
	    {
	      ret = process_query(hostname, ssl_port, query_buf, query, &client_addr);
	    }
	  else
	    {
	      my_error(__FILE__, __LINE__, "unknown request type %d", request_type);
	      exit(ERR_SOCK_SELECT);
	    }

#ifndef ITERATIVE
	  exit(ret);
	}
      /* End of child code */

      if (request_type == REQUEST_HTTPS)
	{
	  close(new_https);
	}
#endif

    }
  return 0; /* never reached */
}
