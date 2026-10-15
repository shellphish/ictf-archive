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
#include <pwd.h>

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
/* #define ITERATIVE */

#define DEFAULT_TCP_PORT "8081"
#define DEFAULT_SSL_PORT "8083"
#define DEFAULT_FILENAME "talkserver.txt"
#define DEFAULT_DOCTITLE "Document"
#define DEFAULT_PASSWD_FILENAME "passwd.txt"
#define DEFAULT_CERT_FILE  "talkserver.pem"
#define DEFAULT_KEY_FILE "talkserver.key"
#define NOTE_PREFIX "_note"
#define USER_PREFIX "_user"
#define CHUNK_SIZE 512
#define COOKIE_SIZE 256
#define DIRBUF_SIZE 256
#define LINE_SIZE 512
#define ANONYMOUS_ACCOUNT "anonymous"
 
/* Parameters: protocol */
#define WELCOME_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head>\n\
    <title>talkserver</title>\n\
  </head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1><tt>talkserver</tt></h1>\n\
    <p>Welcome to <tt>talkserver</tt>, a web-based annotation system.<p>\n\
    <p>You can retrieve the document being discussed by requesting the\n\
    <a href=\"doc\"><tt>/doc</tt></a> resource. You can also see the annotated document\n\
    by requesting the <a href=\"notes\"><tt>/notes</tt></a> resource.</p>\n\
    </p>If you want to upload a comment, first you have to login using\n\
    the <a href=\"login\"><tt>/login</tt></a> form.</p>\n\
    <p>If your username and password are correct, you can upload a comment\n\
    using the <a href=\"note\"><tt>/note</tt></a> form.</p>\n\
    <p>When you have terminated your session, please logout using the\n\
    <a href=\"logout\"><tt>/logout</tt></a> form.</p>\n\
    <p><i>Enjoy!</i>\n\
  </body>\n\
</html>\n"  

/* Parameters: protocol, doctitle, doctitle, doc */
#define DOC_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head>\n\
    <title>%s</title>\n\
  </head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1>%s</h1>\n\
    <pre>%s</pre>\n\
  </body>\n\
</html>\n"  

/* Parameters: protocol, doctitle, doctitle, annotated doc */
#define NOTES_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head>\n\
    <title>Annotated %s</title>\n\
  </head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1>Annotated %s</h1>\n\
    <pre>%s</pre>\n\
  </body>\n\
</html>\n"  

/* Parameters: protocol, hostname, SSL port */
#define LOGIN_FORM_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
<head>\n\
  <title>talkserver login form</title>\n\
</head>\n\
<body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1><tt>talkserver</tt> login form</h1>\n\
    <form action=\"https://%s:%s/credentials\" method=\"get\">\n\
      <p><label for=\"username\">Username:</label>\n\
	<input type=\"text\" name=\"username\" id=\"username\" /></p>\n\
      <p><label for=\"password\">Password: </label>\n\
	<input type=\"password\" name=\"password\" id=\"password\" /></p>\n\
      <p><input type=\"submit\" value=\"login\" /></p>\n\
    </form>\n\
</body>\n\
</html>\n"

/* Parameters: protocol, hostname, SSL port */
#define LOGOUT_FORM_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
<head>\n\
  <title>talkserver logout</title>\n\
</head>\n\
<body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1><tt>talkserver</tt> logout</h1>\n\
    <p>Are you sure you want to logout?</p>\n\
    <form action=\"https://%s:%s/logoff\" method=\"get\">\n\
      <p><input type=\"submit\" value=\"logout\" /></p>\n\
    </form>\n\
</body>\n\
</html>\n"

/* Parameters: protocol, hostname, SSL port */
#define NOTE_FORM_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
<head>\n\
  <title>talkserver note form</title>\n\
</head>\n\
<body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1><tt>talkserver</tt> note form</h1>\n\
    <form action=\"https://%s:%s/postnote\" method=\"post\">\n\
      <p><label for=\"line\">Line:</label>\n\
	<input type=\"text\" size=\"5\" name=\"line\" id=\"line\" /></p>\n\
       <p><label for=\"character\">Character: </label>\n\
	<input type=\"text\" size=\"5\" name=\"character\" id=\"character\" /></p>\n\
       <p>Note</p>\n\
       <p><textarea name=\"note\" id=\"note\" rows=\"20\" cols=\"80\"></textarea></p>\n\
      <p><input type=\"submit\" value=\"submit\" />\n\
         <input type=\"reset\" value=\"reset\" /></p>\n\
    </form>\n\
</body>\n\
</html>\n"

/* Parameters: protocol, cookie, username, hostname, http port */
#define CREDENTIALS_REPLY "%s 200 OK\r\n\
Set-Cookie: User=\"%s\"; Secure\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
<head>\n\
  <title>Login succeeded</title>\n\
</head>\n\
<body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1>Login succeeded for user <tt>%s</tt></h1>\n\
      <p>Proceed to form <a href=\"http://%s:%s/note\"><tt>/note</tt></a>\n\
      to submit annotations.</p>\n\
</body>\n\
</html>\n"

/* Parameters: protocol */
#define BAD_CREDENTIALS_REPLY "%s 403 Forbidden\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>403 Bad Credentials</title></head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\"><h1>403 Bad Credentials</h1></body>\n\
</html>\n"  

/* Parameters: protocol, hostname, port */
#define NOTE_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
<head>\n\
  <title>Note accepted</title>\n\
</head>\n\
<body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1>Note accepted</h1>\n\
    <p>Proceed to <a href=\"http://%s:%s/notes?username=%s\">/notes</a> to review the current annotated document.</p>\n\
</body>\n\
</html>\n"

/* Parameters: protocol */
#define BAD_NOTE_REPLY "%s 403 Forbidden\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>403 Note Refused</title></head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\"><h1>403 Note Refused</h1></body>\n\
</html>\n"  

/* Parameters: protocol */
#define LOGOFF_REPLY "%s 200 OK\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
<head>\n\
  <title>Logout successful</title>\n\
</head>\n\
<body text=\"#ffffff\" bgcolor=\"#6699ff\">\n\
    <h1>Logout successful</h1>\n\
    <p>Thank you for using <tt>talkserver</tt></p>\n\
</body>\n\
</html>\n"

/* Parameters: protocol */
#define BAD_LOGOFF_REPLY "%s 403 Forbidden\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>403 Logout Refused</title></head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\"><h1>403 Logout Refused</h1></body>\n\
</html>\n"  

/* Parameters: protocol */
#define UNKNOWN_METHOD_REPLY "%s 405 Method Not Allowed\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>405 Method Not Allowed</title></head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\"><h1>405 Method Not Allowed</h1></body>\n\
</html>\n"  

/* Parameters: none */
#define BAD_REQUEST_REPLY "HTTP/1.1 401 Bad Request\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>401 Bad Request</title></head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\"><h1>401 Bad Request</h1></body>\n\
</html>\n"  

/* Parameter: protocol */
#define RESOURCE_NOT_FOUND_REPLY "%s 404 File Not Found\r\n\
Content-Type: text/html\r\n\
Cache-Control: no-cache\r\n\
Cache-Control: no-store\r\n\
\r\n\
<html>\n\
  <head><title>404 Resource Not Found</title></head>\n\
  <body text=\"#ffffff\" bgcolor=\"#6699ff\"><h1>404 Resource Not Found</h1></body>\n\
</html>\n"

/* Error codes */
#define ERR_WRONG_PARAMS 1
#define ERR_FILE_OPEN 2
#define ERR_FILE_READ 3
#define ERR_MEMORY 4
#define ERR_FILE_PARSE 5
#define ERR_SOCK_CREATE 6
#define ERR_SOCK_SELECT 7
#define ERR_FORK 8
#define ERR_SSL_INIT 9
#define ERR_SOCK_READ 10
#define ERR_SOCK_WRITE 11
#define ERR_SSL_READ 12
#define ERR_SSL_WRITE 13
#define ERR_PARSE_HTTP 14
#define ERR_WRONG_METHOD 15
#define ERR_NO_COOKIE 16
#define ERR_BAD_COOKIE 17

#define MACOSX_COMPILE
/*
 * DATA STRUCTURES
 */
struct user {
  char* username;
  char* password;
  char* cookie;
  struct user *prev;
  struct user *next;
};


struct http_request {
  char *method;
  char *resource;
  char *protocol;
  char *header;
  /* char *body; */
};

struct annotation {
  char *user;
  int line;
  int character;
  char *note;
  struct annotation *prev;
  struct annotation *next;
};

/*
 * GLOBALS
 */
char hostname[MAXHOSTNAMELEN];
char *tcp_port = DEFAULT_TCP_PORT;
char *ssl_port = DEFAULT_SSL_PORT;
int active_only = 0;
char *passwd = DEFAULT_PASSWD_FILENAME;

/*
 * FUNCTIONS
 */
#ifdef DROPPRIV
static int changeGroup(const char* username, uid_t* ret_uid) {
 struct passwd * pwd = NULL;
 int err;
 uid_t uid = atoi(username);

 if(getuid()) {
  return 0;
 }

 pwd = getpwnam(username);
 if(!pwd && uid) {
  pwd = getpwuid(uid);
 }
 if(!pwd) {
  return 0;
 }

#ifndef MACOSX_COMPILE
 err = setresgid(pwd->pw_gid,pwd->pw_gid,pwd->pw_gid);
 if(err == -1) {
  return 0;
 }

 err = setgroups(1 , &pwd->pw_gid);
 if(err == -1) {
  return 0;
 }
#endif

 *ret_uid = pwd->pw_uid;

 return 1;
}

static int changeUser(uid_t uid) {
 int err;
#ifndef MACOSX_COMPILE
 err = setresuid(uid, uid, uid);
 if(err == -1) {
  return 0;
 }
#endif
 return 1;
}
#endif


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


char *
getline_nocrlf_ssl(SSL *ssl)
{
  char *line = NULL;
  char *str = NULL;
  int ret = 0;
  int line_size = 0;
  int index = 0;
  int i = 0;
  char c = 0;
  
  assert(ssl);

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
      ret = SSL_read(ssl, &c, 1);
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

char *
get_cookie_by_user(char* username)
{
  int fd = 0;
  int ret = 0;
  char *cookie = NULL;
  char userfile[256];

  assert(username);

  sprintf(userfile, "%s.%s", USER_PREFIX, username);

  if ((fd = open(userfile, 
		 O_RDONLY | 
		 O_NONBLOCK,
		 0)) < 0)
    {
      my_error(__FILE__, __LINE__, "can't open cookie file %s",
	       username);
      return NULL;
    }

  if ((cookie = malloc(COOKIE_SIZE)) == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }
  
  if ((ret = read(fd, cookie, COOKIE_SIZE)) < 0)
    {
      my_error(__FILE__, __LINE__, "cookie file %s cannot be read",
	       username);
      free(cookie);
      return NULL;
    }
  cookie[ret] = '\0';

  flock(fd, LOCK_UN);
  close(fd);

  
  return cookie;
}

/* Opens a file and puts the contents into memory 
   Returns a malloc'ed buffer that has to be freed with free */
char *
file_to_buf(char *filename)
{
  int fd = 0;
  int filesize = 0;
  int ret = 0;
  char *buf = NULL;

  assert(filename);

  /* Opens the document file */
  fd = open(filename, O_RDONLY, 0);

  if (fd < 0)
    {
      my_error(__FILE__, __LINE__, "file %s not found", filename);
      return NULL;
    }
  
  filesize = lseek(fd, 0, SEEK_END);

  if (filesize < 0)
    {
      my_error(__FILE__, __LINE__, "cannot determine the size of file %s", filename);
      return NULL;
    }

  buf = (char *)malloc(filesize + 1);
  if (buf == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }

  lseek(fd, 0, SEEK_SET);
  ret = read(fd, buf, filesize);

  if (ret < filesize)
    {
      my_error(__FILE__, __LINE__, 
	       "read failed and returned %d when reading file %s (%d)", ret,
	       filename, filesize);
      free(buf);
      return NULL;
    }

  close(fd);
  buf[filesize] = '\0';

  return buf;
}

int 
parse_users(struct user *users, char *buf)
{
  int userstart = 0;
  int userend = 0;
  int pwdstart = 0;
  int pwdend = 0;
  int i = 0, j = 0;
  int len = 0;
  struct user *new_user = NULL;

  assert(users);
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
      userstart = i;
      while (!isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      userend = i; 
      while (isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      pwdstart =i;
      while (!isspace(buf[i]))
	{
	  i++;
	  CHECK(i);
	}
      pwdend = i; 
      
      new_user = malloc(sizeof(struct user));
      if (new_user == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  return ERR_MEMORY;
	}
      new_user->username = malloc((userend - userstart) + 1);
      if (new_user->username == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  return ERR_MEMORY;
	}

      for (j = userstart; j < userend; j++)
	{
	  new_user->username[j - userstart] = buf[j];
	}
      new_user->username[j - userstart] = '\0';
	
      new_user->password = malloc((pwdend - pwdstart) + 1);
      if (new_user->password == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  return ERR_MEMORY;
	}
      for (j = pwdstart; j < pwdend; j++)
	{
	  new_user->password[j - pwdstart] = buf[j];
	}
      new_user->password[j - pwdstart] = '\0';

      new_user->prev = users->prev;
      users->prev->next = new_user;
      users->prev = new_user;
      new_user->next = users;
      
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, 
	       "created user \"%s\" with password \"%s\"", 
	       new_user->username, new_user->password);
#endif

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
  struct http_request *request = NULL;

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
  
  free(r);
  return;
}  
struct user *
check_credentials(struct http_request *r, struct user *users)
{
  char cmd[512];
  char *username = NULL;
  char *password = NULL;
  char cookie[COOKIE_SIZE];
  char userfile[256];
  struct user *user = NULL;
  struct user *new_user = NULL;
  struct timeval t = {0,0};
  int fd = 0;
  
  assert(r);
  assert(users);

  username = strchr(r->resource, '?');
  if (username == NULL)
    {
      my_error(__FILE__, __LINE__, "credentials without parameters");
      return NULL;
    }

  username++;
  if (strncmp(username, "username=", strlen("username=")))
    {
      my_error(__FILE__, __LINE__, "credentials without username parameter");
      return NULL;
    }
  username += strlen("username=");
  password = strchr(username, '&');
  if (password == NULL)
    {
      my_error(__FILE__, __LINE__, "credentials without password");
      return NULL;
    }
  password[0] = '\0';
  password++;

  if (strncmp(password, "password=", strlen("password=")))
    {
      my_error(__FILE__, __LINE__, "credentials without password");
      return NULL;
    }
  password = password + strlen("password=");

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, 
	   "authenticating user [%s] password [%s]", 
	   username, password);
#endif

  for (user = users->next; user != users; user = user->next)
    {
      if (!strcmp(user->username, username) &&
	  !strcmp(user->password, password))
	{
	  break;
	}
    }
   if (user == users)
     {

       /* Creates a new user */
       if ((strchr(username, ' ')) || 
	   (strchr(username, ';')) || 
	   (strchr(username, '&')))
	 {
	   return NULL;
	 }
       if ((strchr(password, ' ')) || 
	   (strchr(password, ';')) || 
	   (strchr(password, '&')))
	 {
	   return NULL;
	 }
       sprintf(cmd, "echo %s %s >> %s", username, password, passwd);
       system(cmd);

       new_user = malloc(sizeof(struct user));
       user->username = strdup(username);
       user->password = strdup(password);

       new_user->prev = users->prev;
       users->prev->next = new_user;
       users->prev = new_user;
       new_user->next = users;

#ifdef DEBUG
      my_debug(__FILE__, __LINE__, 
	       "created user \"%s\" with password \"%s\"", 
	       new_user->username, new_user->password);
#endif
     }
   
   gettimeofday(&t, NULL);
   
   snprintf(cookie, COOKIE_SIZE, "%s:%lu", 
	    user->username, (unsigned long)t.tv_sec);
   
   sprintf(userfile, "%s.%s", USER_PREFIX, user->username);
   
   if ((fd = open(userfile, 
		  O_RDWR | 
		  O_CREAT |
		  O_TRUNC |
		  O_NONBLOCK,
		  S_IRUSR | S_IWUSR)) < 0)
     {
       my_error(__FILE__, __LINE__, "can't open cookie file %s",
		userfile);
       return NULL;
     }
   if (write(fd, cookie, strlen(cookie)) < 0)
     {
       my_error(__FILE__, __LINE__, "cannot write cookie %s to file %s",
		cookie, user->username);
       
       return NULL;
     }

   flock(fd, LOCK_UN);
   close(fd);
   user->cookie = strdup(cookie); 
   return user;
}

struct user *
get_user_by_cookie(char *cookie, struct user *users)
{
  char *username = NULL;
  char *end = NULL;
  char *stored_cookie = NULL;
  struct user *user = NULL;

  assert(cookie);
  assert(users);

  username = strdup(cookie);
  if (username == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      goto end;
    }
  
  if ((end = strchr(username, ':')) == NULL) 
    {
      my_error(__FILE__, __LINE__, "malformed cookie %s", cookie);
      goto end;
    }

  *end = '\0';

  stored_cookie = get_cookie_by_user(username);
  if (stored_cookie == NULL)
    {
      my_error(__FILE__, __LINE__, 
	       "could not find cookie for user %s", username);
      goto end;
    }
  if (strcmp(stored_cookie, cookie))
    {
      my_error(__FILE__, __LINE__, 
	       "cookie %s does not match stored cookie %s",
	       cookie, stored_cookie);
      goto end;
    }
  
  for (user = users->next; user != users; user = user->next)
    {
      if (!strcmp(user->username, username))
	{
	  return user;
	}
    }
  
 end:
  if (stored_cookie) free(stored_cookie);
  if (username) free(username);
  return NULL;
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

struct http_request*
parse_http_request(int http)
{
  struct http_request *r = NULL;
  char *data = NULL;
  int data_size = 0;
  int index = 0;
  char c = 0;
  int ret = 0;

  data_size = CHUNK_SIZE;
  if ((data = (char *)malloc(data_size)) == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }

  while (1)
    {
      ret = read(http, &c, 1);
      /* EOF */
      if (ret == 0)
	{
	  break;
	}
      /* ERROR */
      if (ret < 0)
	{
	  free(data);
	  return NULL;
	}
      data[index] = c;
      index++;
      data[index] = '\0';

      if (index == data_size - 2)
	{
	  data_size += CHUNK_SIZE;
	  if ((data = (char *)realloc(data, data_size)) == NULL)
	    {
	      my_error(__FILE__, __LINE__, "realloc failed");
	      free(data);
	      return NULL;
	    }
	}
      if (!strcmp(&(data[index - 4]), "\r\n\r\n"))
	{
	  break;
	}
    }

  r = parse_request(data);
  free(data);
  return r;
}


struct annotation *
load_note(char *fname, char* username, struct user *users)
{
  struct annotation *annotation = NULL;
  char *buf = NULL;
  struct user *u = NULL;
  char *author = NULL;
  char *cookie = NULL;
  char *line = NULL;
  char *character = NULL;
  char *note = NULL;
  char *stored_cookie = NULL;
  int found = 0;

  assert(fname);
  assert(users);

  /* Loads the file into memory: buf needs to be free()-ed */
  if ((buf = file_to_buf(fname)) == NULL)
    {
      my_error(__FILE__, __LINE__, "cannot load note %s", fname);
      return NULL;
    }

  /* Parses the file */
  author = buf;
  if ((cookie = strchr(author, '\n')) == NULL) goto end;
  cookie[0] = '\0';
  cookie++;

  if ((line = strchr(cookie, '\n')) == NULL) goto end;
  line[0] = '\0';
  line++;

  if ((character = strchr(line, '\n')) == NULL) goto end;
  character[0] = '\0';
  character++;

  if ((note = strchr(character, '\n')) == NULL) goto end;
  note[0] = '\0';
  note++;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "loaded note\n\tauthor [%s]\n\tcookie [%s]\n\tline [%s]\n\tcharacter [%s]\n\tnote [%s]", 
	   author, cookie, line, character, note);
#endif

  /* Checks if the user exists */
  found = 0;
  for (u = users->next; u != users; u = u->next)
    {
      if (!strcmp(u->username, author))
	{
	  found = 1;
	  break;
	}
    }
  if (found == 0) goto end;

  /* Checks if the user matches */
  if (strcmp(username, author)) 
    {
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, 
	       "note by author [%s] cannot be shown to user [%s]", 
	       author, username);
#endif
      
      goto end; 
    }
  if (active_only)
    {
      /* Checks if the annotation is associated with an active cookie */
      if ((stored_cookie = get_cookie_by_user(username)) == NULL) goto end;

      if (strcmp(cookie, stored_cookie)) 
	{
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, 
		   "current cookie [%s] does not match annotation cookie [%s]", 
		   stored_cookie, cookie);
#endif
	  
	  goto end;
	}
    }

  annotation = malloc(sizeof(struct annotation));
  if (annotation == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      goto end;
    }

  if ((annotation->user = strdup(username)) == NULL) goto failed;
  if ((annotation->line = atoi(line)) <= 0) goto failed;
  if ((annotation->character = atoi(character)) <= 0)  goto failed;
  if ((annotation->note = strdup(note)) == NULL)  goto failed; 

  goto end;

 failed:
  if (annotation->user) free(annotation->user);
  if (annotation->note) free(annotation->note);
  free(annotation);
  annotation = NULL;

 end:  
  if (buf) free(buf);
  if (stored_cookie) free(stored_cookie);
  return annotation;
}

int
get_notes(int dirfd, char *username, struct user *users, struct annotation *annotations)
{
  struct dirent *dirent = NULL;
  char *dirbuf = NULL;
  char *dirent_p = NULL;
  struct annotation *annotation = NULL;
  struct annotation *curr = NULL;
  int ret = 0;
  long basep = 0;
  int notes_size = 0;

  assert(users);
  assert(annotations);

  dirbuf = malloc(DIRBUF_SIZE);
  if (dirbuf == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return 0;
    }
  ret = 0;

  while (1)
    {
      if ((ret = getdirentries(dirfd, dirbuf, DIRBUF_SIZE, &basep)) < 0)
	{
	  my_error(__FILE__, __LINE__, "cannot get dir entries");
	  return 0;
	}
      if (ret == 0) break;

#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "read %d bytes of dir entries", ret);
#endif      
      dirent_p = dirbuf;
      while (1)
	{
	  dirent = (struct dirent *)dirent_p;

#ifdef DEBUG2
	  my_debug(__FILE__, __LINE__, "found dir entry\n\tfileno %ul\n\td_reclen %d\n\td_type %d\n\td_namlen %d\n\td_name %s", 
		   dirent->d_fileno,
		   dirent->d_reclen,
		   dirent->d_type,
		   dirent->d_namlen,
		   dirent->d_name);
#endif      
	  
	  if ((dirent->d_type != 8) || 
	      (strncmp(dirent->d_name, NOTE_PREFIX, strlen(NOTE_PREFIX))))
	    {
	      dirent_p += dirent->d_reclen; 
	      if (dirent_p >= dirbuf + ret) 
		break;
	      continue;
	    }

#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "found note %s", dirent->d_name);
#endif      

	  if ((annotation = load_note(dirent->d_name, username, users)))
	    {
	      curr = annotations->next;
	      while (curr != annotations)
		{
		  if (curr->line < annotation->line)
		    {
		      curr = curr->next;
		      continue;
		    }
		  if ((curr->line == annotation->line) && (curr->character < annotation->character))
		    {
		      curr = curr->next;
		      continue;
		    }
		  break;
		}
	      annotation->prev = curr->prev;
	      curr->prev = annotation;
	      annotation->next = curr;
	      annotation->prev->next = annotation;
	      notes_size += strlen(annotation->note);
	      notes_size += strlen(annotation->user);
	      notes_size += strlen("[:]");
	    }
	  dirent_p += dirent->d_reclen; 
	  if (dirent_p >= dirbuf + ret) 
	    break;
	}
    }

#ifdef DEBUG
  for (curr = annotations->next; curr != annotations; curr = curr->next)
    my_debug(__FILE__, __LINE__, "note: user [%s] line [%d] character [%d] note [%s]", 
	     curr->user, curr->line, curr->character, curr->note);
#endif
  
  
  return notes_size;
}

char *
insert_note(char* buf, struct annotation *n)
{
  int i = 0;

  assert(buf);
  assert(n);

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "including note\n\tuser [%s]\n\tline [%d]\n\tcharacter [%d]\n\tnote [%s]", 
	   n->user, n->line, n->character, n->note);
#endif
	   
  *buf = '[';
  buf++;
  for (i = 0; i < strlen(n->user); i++)
    {
      *buf = n->user[i];
      buf++;
    }
  *buf = ':';
  buf++;
  for (i = 0; i < strlen(n->note); i++)
    {
      *buf = n->note[i];
      buf++;
    }
  *buf = ']';
  buf++;

  return buf;
}

int 
process_http_request(struct user *users, char *doc, char* doctitle, int http)
{
  /* This function implements:
     GET /
     GET /login
     GET /logout
     GET /doc
     GET /notes
     GET /note
  */

  struct http_request *r = NULL;
  char *reply = NULL;
  int replysize = 0;
  int ret = 0;
  int dirfd = 0;
  int doc_index = 0;
  char *andoc_p = NULL;
  int character = 0;
  int line = 0;
  char *annotated_doc = NULL;
  char *str = NULL;
  struct annotation annotations;
  struct annotation *n = NULL;
  char *username = NULL;

  assert(users);
  assert(doc);
  assert(doctitle);

  annotations.next = &annotations;
  annotations.prev = &annotations;

  r = parse_http_request(http);

  if (r == NULL)
    {
      write(http, BAD_REQUEST_REPLY, strlen(BAD_REQUEST_REPLY));
      ret = ERR_PARSE_HTTP;
      goto end; 
    }

#ifdef DEBUG
  str = request_to_str(r);
  my_debug(__FILE__, __LINE__, "received request\n%s", str);
  free(str);
#endif

  /* Welcome message */
  if (!strcmp(r->resource, "/"))
    {
      replysize = strlen(WELCOME_REPLY) + strlen(r->protocol) + 1;
      reply = (char *)malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, WELCOME_REPLY, r->protocol);
    }
  else if (!strcmp(r->resource, "/doc"))
    {
      replysize = strlen(DOC_REPLY) + strlen(r->protocol) +
	strlen(doctitle) + strlen(doctitle) + strlen(doc) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, DOC_REPLY, r->protocol, doctitle, doctitle, doc);
    }
  else if (!strcmp(r->resource, "/login"))
    {
      replysize = strlen(LOGIN_FORM_REPLY) + strlen(r->protocol) +
	strlen(hostname) + strlen(ssl_port) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, LOGIN_FORM_REPLY, r->protocol, hostname, ssl_port);
    }
  else if (!strcmp(r->resource, "/note"))
    {
      replysize = strlen(NOTE_FORM_REPLY) + strlen(r->protocol) +
	strlen(hostname) + strlen(ssl_port) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, NOTE_FORM_REPLY, r->protocol, hostname, ssl_port);
    }
  else if (!strncmp(r->resource, "/notes", strlen("/notes")))
    {
      /* Parses the string, looking for parameters */
      username = strchr(r->resource, '?');
      if (username == NULL)
	{
	  username = ANONYMOUS_ACCOUNT;
	}
      else
	{
	  username++;
	  if (strncmp(username, "username=", strlen("username=")))
	    {
	      my_error(__FILE__, __LINE__, "credentials without username parameter");
	      goto end;
	    }
	  username += strlen("username=");
	}
      /* Opens current directory */
      if ((dirfd = open(".", O_RDONLY, 0)) < 0)
	{
	  my_error(__FILE__, __LINE__, "cannot open local dir");
	  ret = ERR_FILE_OPEN;
	  goto end;
	}

      /* Fills in the annotation list and returns size of 
	 annotations */
      ret = get_notes(dirfd, username, users, &annotations);
      close(dirfd);
      if (ret < 0)
	{
	  my_error(__FILE__, __LINE__, "could not retrieve annotations");
	  ret = ERR_FILE_READ;
	  goto end;
	}

      /* Allocates document size */
      annotated_doc = malloc(strlen(doc) + ret);
      if (annotated_doc == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}

      /* Fills in the annotated doc */
      doc_index = 0;
      andoc_p = annotated_doc;
      line = 1;
      character = 1;
      n = annotations.next;
      while (doc_index < strlen(doc))
	{
#ifdef DEBUG2
	  my_debug(__FILE__, __LINE__, "Line: %d, Char: %d, Index: %d (%c)", 
		   line, character, doc_index, doc[doc_index]);
#endif

	  if ((n != &annotations) && (n->line == line) && (n->character == character))
	    {
	      /* Inserts annotation and advances andoc_p */
	      andoc_p = insert_note(andoc_p, n);
	      n = n->next;
	      continue;
	    }
	  *andoc_p = doc[doc_index];
	  andoc_p++;
	  doc_index++;
	  character++;
	  if (doc[doc_index] == '\n')
	    {
	      while ((n != &annotations) && (n->line == line))
		{
		  andoc_p = insert_note(andoc_p, n);
		  n = n->next;
		}
	      *andoc_p = doc[doc_index];
	      andoc_p++;
	      doc_index++;
	      character = 1;
	      line++;
	    }
	}
      while (n != &annotations)
	{
	  andoc_p = insert_note(andoc_p, n);
	  n = n->next;
	}

      *andoc_p = 0;

      replysize = strlen(NOTES_REPLY) + strlen(r->protocol) +
	strlen(doctitle) + strlen(doctitle) + strlen(annotated_doc) +  1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, NOTES_REPLY, r->protocol, doctitle, doctitle, annotated_doc);
    }
  else if (!strcmp(r->resource, "/logout"))
    {
      replysize = strlen(LOGOUT_FORM_REPLY) + strlen(r->protocol) +
	strlen(hostname) + strlen(ssl_port) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, LOGOUT_FORM_REPLY, r->protocol, hostname, ssl_port);
    }
  else
    {
      replysize = strlen(RESOURCE_NOT_FOUND_REPLY) + strlen(r->protocol) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, RESOURCE_NOT_FOUND_REPLY, r->protocol);
    }

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "sending reply [%s]", reply);
#endif
  
  ret = write(http, reply, strlen(reply));
  if (ret < strlen(reply))
    {
      my_error(__FILE__, __LINE__, "can't write to socket");
      ret = ERR_SOCK_WRITE;
      goto end;
    }
  
  ret = 0;
 end:
  if (reply) free(reply);
  if (annotated_doc) free(annotated_doc);
  for (n = annotations.next; n != &annotations; n = n->next) free(n);
  close(http);

  return ret;
}

char *
get_cookie(struct http_request *r)
{
  char *cookie = NULL;
  char *user = NULL;
  char *buf = NULL;
  int i = 0;

  assert(r);
  assert(r->header);

  cookie = strcasestr(r->header, "\r\nCookie:");
  if (cookie == NULL)
    {
#ifdef DEBUG
      my_error(__FILE__, __LINE__, "can't find cookie in %s", r->header);
#endif
      return NULL;
    }
  user = strcasestr(cookie, "User=");
  if (user == NULL)
    {
#ifdef DEBUG
      my_error(__FILE__, __LINE__, "can't find user field in %s", cookie);
#endif
      return NULL;
    }
  user += strlen("User=");
  if (user[0] == '"') 
    {
      user++;
    }
  
  if (strstr(cookie, "\r") == NULL)
    {
#ifdef DEBUG
      my_error(__FILE__, __LINE__, "can't find user end in %s", user);
#endif
      return NULL;
    }  
  buf = malloc(COOKIE_SIZE);
  if (buf == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }
  i = 0;
  while(user[i] != '\r')
    {
      buf[i] = user[i];
      i++;
      if (i == COOKIE_SIZE - 1) break;
    }
  buf[i] = '\0';
  if (buf[i - 1] == '"')
    {
      buf[i - 1] = '\0';
    }
      
  return buf;
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

  content = strcasestr(r->header, "\r\nContent-Length:");
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



int
process_note(struct http_request *r, struct user *users, SSL *ssl, char* author)
{
  char *cookie = NULL;
  struct user *user = NULL;
  int found = 0;
  char *body = NULL;
  int body_size = 0;
  int ret = 0;
  int index = 0;
  char c = 0;
  char *character = NULL;
  char character_str[MAXNUMSTRING];
  char *line = NULL;
  char line_str[MAXNUMSTRING];
  char *note = NULL;
  int i = 0;
  int fd = 0;
  char tmpfile[16];

  assert(r);
  assert(r->method);
  assert(users);
  assert(ssl);
    
  /* Checks that POST has been used */
  if (strcmp(r->method, "POST"))
    {
      my_error(__FILE__, __LINE__, "wrong method %s", r->method);
      return ERR_WRONG_METHOD;
    }

  /* Extracts the cookie (needs to be free()-ed) */
  if ((cookie = get_cookie(r)) == NULL)
    {
      ret =  ERR_NO_COOKIE;
      goto end;
    }

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "found request cookie [%s]", cookie);
#endif
  
  found = 0;
  /* Checks that there is a user with that cookie */
  user = get_user_by_cookie(cookie, users);
  if (user == NULL)
    {
      my_error(__FILE__, __LINE__, "no user with cookie %s", cookie);
      ret = ERR_BAD_COOKIE;
      goto end;
    }
  
  if ((body_size = get_body_size(r)) < 0)
    {
      my_error(__FILE__, __LINE__, "unknown body length");
      ret = ERR_PARSE_HTTP;
      goto end;
    }
  
  /* Gets the body (needs tp be free()-ed) */
  if ((body = (char *)malloc(body_size + 1)) == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      ret = ERR_MEMORY;
      goto end;
    }
  
  index = 0;
  while (index < body_size)
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
	  free(body);
	  return ERR_SSL_READ;
	}
  
      body[index] = c;
      index++;
      body[index] = '\0';
    }
  
  /* Parses the body */
#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "body of request is [%s]", body);
#endif

  if((line = strstr(body, "line=")) == NULL)
    {
      ret = ERR_PARSE_HTTP;
      goto end;
    }
  line += strlen("line=");
  if (strchr(line, '&') == NULL)
    {
      ret = ERR_PARSE_HTTP;
      goto end;
    }
  i = 0;
  while (line[i] != '&')
    {
      line_str[i] = line[i];
      i++;
      if (i == MAXNUMSTRING)
	{
	  ret = ERR_PARSE_HTTP;
	  goto end;
	}
    }
  line_str[i] = '\0';
  
  if((character = strstr(body, "character=")) == NULL)
    {
      ret = ERR_PARSE_HTTP;
      goto end;
    }
  character += strlen("character=");
  if (strchr(character, '&') == NULL)
    {
      ret = ERR_PARSE_HTTP;
      goto end;
    }
  i = 0;
  while (character[i] != '&')
    {
      character_str[i] = character[i];
      i++;
      if (i == MAXNUMSTRING)
	{
	  ret = ERR_PARSE_HTTP;
	  goto end;
	}
    }
  character_str[i] = '\0';

  if((note = strstr(body, "note=")) == NULL)
    {
      ret = ERR_PARSE_HTTP;
      goto end;
    }
  note += strlen("note=");

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, 
	   "line is [%s], character is [%s], note is [%s]", 
	   line_str, character_str, note);
#endif

  sprintf(tmpfile, "%s.XXXXXX", NOTE_PREFIX);

  /* Temp, unique file. No need to lock */
  if ((fd = mkstemp(tmpfile)) < 0)
    {
      ret = ERR_FILE_OPEN;
      goto end;
    }

  write(fd, user->username, strlen(user->username));
  write(fd, "\n", 1);
  write(fd, cookie, strlen(cookie));
  write(fd, "\n", 1);
  write(fd, line_str, strlen(line_str));
  write(fd, "\n", 1);
  write(fd, character_str, strlen(character_str));
  write(fd, "\n", 1);
  write(fd, note, strlen(note));

  close(fd);
  sprintf(author, user->username);
  ret = 0;

 end:
  if (body) free (body);
  if (cookie) free(cookie);
  return ret;
}

int
process_logoff(struct http_request *r, struct user *users, SSL *ssl)
{
  char *cookie = NULL;
  struct user *user = NULL;

  assert(r);
  assert(users);
  assert(ssl);

  /* Extracts the cookie from the request */
  cookie = get_cookie(r);
  if (cookie == NULL)
    {
      my_error(__FILE__, __LINE__, "request is missing cookie");
      return ERR_BAD_COOKIE;
    }
  
  /* Checks that there is a user with that cookie */
  user = get_user_by_cookie(cookie, users);
  if (user == NULL)
    {
      my_error(__FILE__, __LINE__, "no user with cookie %s", cookie);
      return ERR_BAD_COOKIE;
    }
  
  /* Deletes the cookie file */
  unlink(user->username);

  return 0;
}

struct http_request*
parse_ssl_request(SSL *ssl)
{
  struct http_request *r = NULL;
  char *data = NULL;
  int data_size = 0;
  int index = 0;
  char c = '\0';
  int ret = 0;

  assert(ssl);

  data_size = CHUNK_SIZE;
  if ((data = (char *)malloc(data_size)) == NULL)
    {
      my_error(__FILE__, __LINE__, "not enough memory");
      return NULL;
    }

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
	  free(data);
	  return NULL;
	}
      data[index] = c;
      index++;
      data[index] = '\0';

      if (index == data_size - 2)
	{
	  data_size += CHUNK_SIZE;
	  if ((data = (char *)realloc(data, data_size)) == NULL)
	    {
	      my_error(__FILE__, __LINE__, "realloc failed");
	      free(data);
	      return NULL;
	    }
	}
      if (!strcmp(&(data[index - 4]), "\r\n\r\n"))
	{
	  break;
	}
    }

  r = parse_request(data);
  free(data);
  return r;
}

int 
process_https_request(struct user *users, char *doc, char* doctitle, int https)
{
  /* This function implements:
     GET /
     GET /credentials?user=<username>&password=<password>
     POST /postnote (+cookie)
     GET /logoff (+cookie)
  */

  struct http_request *r = NULL;
  char *reply = NULL;
  int replysize = 0;
  int ret = 0; /* Return value */
  struct user *user = NULL;
  char *str;
  char author[256];
  SSL_CTX* ctx = NULL;
  SSL* ssl = NULL;
  SSL_METHOD *meth = NULL;

  assert(users);
  assert(doc);
  assert(doctitle);

  /* Initializes SSL library */
  SSL_load_error_strings();
  SSL_library_init();

  /* Creates server context */
  if ((meth = SSLv23_server_method()) == NULL)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't set SSL server method");
      ret = ERR_SSL_INIT;
      goto end;
    }
  ctx = SSL_CTX_new(meth);
  if (!ctx) 
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't initialize the SSL context");
      ret = ERR_SSL_INIT;
      goto end;
    }

  /* Sets certificate */
  if (SSL_CTX_use_certificate_file(ctx, 
				   DEFAULT_CERT_FILE, 
				   SSL_FILETYPE_PEM) <= 0) 
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "server certificate not found");
      ret = ERR_SSL_INIT;
      goto end;
    }

  /* Sets private key */
  if (SSL_CTX_use_PrivateKey_file(ctx, 
				  DEFAULT_KEY_FILE, 
				  SSL_FILETYPE_PEM) <= 0) 
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "private key not found");
      ret = ERR_SSL_INIT;
      goto end;
    }
  if (!SSL_CTX_check_private_key(ctx)) 
    {
      my_error(__FILE__, __LINE__, 
	       "private key does not match the certificate's public key");
      ret = ERR_SSL_INIT;
      goto end;
    }

  /* Creates new SSL connection from context */
  ssl = SSL_new(ctx);
  if (ssl == NULL)
    {
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

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "SSL connection using %s\n", 
	   SSL_get_cipher(ssl));
#endif
  
  /* Parses the request (r is malloc()ed and needs to be
     free()ed with free_request() */
  r = parse_ssl_request(ssl);
  if (r == NULL)
    {
      SSL_write(ssl, BAD_REQUEST_REPLY, strlen(BAD_REQUEST_REPLY));
      ret = ERR_PARSE_HTTP;
      goto end; 
    }

#ifdef DEBUG
  str = request_to_str(r);
  my_debug(__FILE__, __LINE__, "received request\n%s", str);
  free(str);
#endif

  /* Welcome message */
  if (!strcmp(r->resource, "/"))
    {
      replysize = strlen(WELCOME_REPLY) + strlen(r->protocol) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, WELCOME_REPLY, r->protocol);
    }
  else if (!strncmp(r->resource, "/credentials", strlen("/credentials")))
    {
      user = check_credentials(r, users);

      if ((user == NULL) || (user->cookie == NULL))
	{
	  replysize = strlen(BAD_CREDENTIALS_REPLY) + strlen(r->protocol) + 1;
	  reply = malloc(replysize);
	  if (reply == NULL)
	    {
	      my_error(__FILE__, __LINE__, "not enough memory");
	      ret = ERR_MEMORY;
	      goto end;
	    }
	  sprintf(reply, BAD_CREDENTIALS_REPLY, r->protocol);
	}
      else 
	{
	  replysize = strlen(CREDENTIALS_REPLY) + strlen(r->protocol) + 
	    strlen(user->cookie) + strlen(user->username) +
	    strlen(hostname) + strlen(tcp_port) +1;
	  reply = malloc(replysize);
	  if (reply == NULL)
	    {
	      my_error(__FILE__, __LINE__, "not enough memory");
	      ret = ERR_MEMORY;
	      goto end;
	    }
	  sprintf(reply, CREDENTIALS_REPLY, 
		  r->protocol, user->cookie, user->username,
		  hostname, tcp_port);
	  free(user->cookie);
	  user->cookie = NULL;
	}
    }
  else if (!strncmp(r->resource, "/postnote", strlen("/postnote")))
    {  
      author[0] = '\0';
      ret = process_note(r, users, ssl, author);
      
      if (ret != 0)
	{
	  replysize = strlen(BAD_NOTE_REPLY) + strlen(r->protocol) + 1;
	  reply = malloc(replysize);
	  if (reply == NULL)
	    {
	      my_error(__FILE__, __LINE__, "not enough memory");
	      ret = ERR_MEMORY;
	      goto end;
	    }
	  sprintf(reply, BAD_NOTE_REPLY, r->protocol);
	}
      else
	{
	  if (strlen(author) == 0)
	    {
	      sprintf(author, "anonymous");
	    }
	  replysize = strlen(NOTE_REPLY) + strlen(r->protocol) +
	    strlen(hostname) + strlen(tcp_port) + strlen(author) + 1;
	  reply = malloc(replysize);
	  if (reply == NULL)
	    {
	      my_error(__FILE__, __LINE__, "not enough memory");
	      ret = ERR_MEMORY;
	      goto end;
	    }

	  sprintf(reply, NOTE_REPLY, r->protocol, hostname, tcp_port, author);
	}
    }
  else if (!strncmp(r->resource, "/logoff", strlen("/logoff")))
    {
      ret = process_logoff(r, users, ssl);
      
      if (ret != 0)
	{
	  replysize = strlen(BAD_LOGOFF_REPLY) + strlen(r->protocol) + 1;
	  reply = malloc(replysize);
	  if (reply == NULL)
	    {
	      my_error(__FILE__, __LINE__, "not enough memory");
	      ret = ERR_MEMORY;
	      goto end;
	    }
	  sprintf(reply, BAD_LOGOFF_REPLY, r->protocol);
	}
      else
	{
	  replysize = strlen(LOGOFF_REPLY) + strlen(r->protocol) + 1;
	  reply = malloc(replysize);
	  if (reply == NULL)
	    {
	      my_error(__FILE__, __LINE__, "not enough memory");
	      ret = ERR_MEMORY;
	      goto end;
	    }
	  sprintf(reply, LOGOFF_REPLY, r->protocol);
	}
    }
  else
    {
      replysize = strlen(RESOURCE_NOT_FOUND_REPLY) + strlen(r->protocol) + 1;
      reply = malloc(replysize);
      if (reply == NULL)
	{
	  my_error(__FILE__, __LINE__, "not enough memory");
	  ret = ERR_MEMORY;
	  goto end;
	}
      sprintf(reply, RESOURCE_NOT_FOUND_REPLY, r->protocol);
    }

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "sending reply [%s]", reply);
#endif

  ret = SSL_write(ssl, reply, strlen(reply));
  if (ret < 0)
    {
      ERR_print_errors_fp(stderr);
      my_error(__FILE__, __LINE__, "can't write to SSL connection");
      ret = ERR_SSL_WRITE;
      goto end;
    }
  
  ret = 0;
 end:
  if (r) free_request(r);
  if (reply) free(reply);
  if (ssl) SSL_free(ssl);
  if (ctx) SSL_CTX_free(ctx);
  close(https);

  return ret;
}

int 
process_request(struct user *users, char *doc, 
		char* doctitle, int http, int https)
{
  assert(users);
  assert(doc);
  assert(doctitle);

  if (http >= 0)
    {
      return process_http_request(users, doc, doctitle, http);
    }
  else if (https >= 0)
    {
      return process_https_request(users, doc, doctitle, https);
    }
  else
    {
      my_error(__FILE__, __LINE__, 
	       "no valid socket descriptor: http:%d, https:%d", http, https);
      exit(ERR_SOCK_SELECT);
    }
  return 0; /* never reached */
}

int 
main(int argc, char *argv[])
{
  char *doctitle = DEFAULT_DOCTITLE;
  char *doc = NULL;
  char *filename = DEFAULT_FILENAME;
  char *passwdbuf = NULL;
  int i = 0;
  int ret = 0;
  struct user users;
  int http = 0;
  int new_http = 0;
  int https = 0;
  int new_https = 0;
  int max_socket = 0;
  fd_set connections;
  struct sockaddr_in client_addr;
  int client_addr_len = 0;
  struct hostent *hp = NULL;
#ifndef ITERATIVE
  int pid = 0;
#endif
  uid_t new_uid;
  char* arg_username = "talkun";

#ifdef DROPPRIV
  if(arg_username && !changeGroup(arg_username, &new_uid)) {
   fprintf(stderr, "Error setting user %s\n", arg_username);
   exit(1);
  }

  if(arg_username && !changeUser(new_uid)) {
   fprintf(stderr, "Error setting user %s\n", arg_username);
   exit(1);
  }
#endif

  /* Initializes user list pointers */
  users.next = &users;
  users.prev = &users;

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
	  
	  tcp_port = argv[i];
	}
      else if (!strcmp(argv[i], "--sslport"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  ssl_port = argv[i];
	}
      else if (!strcmp(argv[i], "--doc"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  filename = argv[i];
	}
      else if (!strcmp(argv[i], "--users"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  passwd = argv[i];
	}
      else if (!strcmp(argv[i], "--doctitle"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  doctitle = argv[i];
	}
      else if (!strcmp(argv[i], "--hostname"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    my_error(__FILE__, __LINE__, 
		     "missing argument of parameter %s", argv[i - 1]);
	    exit(ERR_WRONG_PARAMS);
	  }
	  
	  strncpy(hostname, argv[i], MAXHOSTNAMELEN);
	}
      else if (!strcmp(argv[i], "--active-only"))
	{
	  i++;
	  active_only = 1;
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
      /* Sets the hostname */
      gethostname(hostname, MAXHOSTNAMELEN);
      
      /* The name is not in full dotted notation */
      if (strchr(hostname, '.') == NULL)
	{
	  hp = gethostbyname(hostname);
	  if (hp == NULL)
	    {
	      my_error(__FILE__, __LINE__, "can't get my hostname, using \"localhost\"");
	      strncpy(hostname, "localhost", MAXHOSTNAMELEN);
	    }
	  else if (strchr(hp->h_name, '.'))
	    {
	      strncpy(hostname, hp->h_name, MAXHOSTNAMELEN);
	    }
	  else 
	    {
	      my_error(__FILE__, __LINE__, "can't get my hostname, using \"localhost\"");
	      strncpy(hostname, "localhost", MAXHOSTNAMELEN);
	    }
	}
    }

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "using hostname: [%s]", hostname);
#endif

  if ((doc = file_to_buf(filename)) == NULL)
    {
      my_error(__FILE__, __LINE__, "cannot load file %s", filename);
      exit(ERR_FILE_READ);
    }

  /* Creates passive TCP socket */
  if ((http = passiveTCP(tcp_port)) < 0)
    {
      my_error(__FILE__, __LINE__, 
	    "can't create server TCP socket on port %s", tcp_port);
      exit(ERR_SOCK_CREATE);
    }

  /* Creates passive SSL socket */
  if ((https = passiveTCP(ssl_port)) < 0)
    {
      my_error(__FILE__, __LINE__, 
	    "can't create server SSL/TCP socket on port %s", ssl_port);
      exit(ERR_SOCK_CREATE);
    }

  /* Waits for a connection on either socket */

  max_socket = 0;
  if (max_socket <= http) 
    max_socket = http + 1;
  if (max_socket <= https)
    max_socket = https + 1;
  
  while (1)
    {
      FD_ZERO(&connections);
      FD_SET(http, &connections);
      FD_SET(https, &connections);
      
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, 
	       "waiting for requests on ports http:%s and https:%s",
	       tcp_port, ssl_port);
#endif
      
      ret = select(max_socket, &connections, NULL, NULL, NULL);
      
      if (ret < 0)
	{
	  if (errno == EINTR)
	    {
	      continue;
	    }
	  else
	    {
	      my_error(__FILE__, __LINE__, "select() on HTTP/HTTPS sockets failed");
	      exit(ERR_SOCK_SELECT);
	    }
	}

      new_http = -1;
      new_https = -1;
      memset(&client_addr, 0, sizeof(client_addr));
      client_addr_len = sizeof(client_addr);

      if (FD_ISSET(http, &connections))
	{
	  new_http = accept(http, 
			    (struct sockaddr *)&client_addr, 
			    &client_addr_len);

	  if (new_http < 0)
	    {
	      my_error(__FILE__, __LINE__, 
		       "accept() on HTTP socket %d failed", http);
	      continue; /* Try all over again */
	    }
	}
      else if (FD_ISSET(https, &connections))
	{
	  new_https = accept(https, 
			     (struct sockaddr *)&client_addr, 
			     &client_addr_len);
	  if (new_https < 0)
	    {
	      my_error(__FILE__, __LINE__, 
		       "accept() on HTTPS socket %d failed", https);
	      continue; /* Try all over again */
	    }
	}
      else
	{
#ifdef DEBUG
	  my_error(__FILE__, __LINE__, "select() did not return any active socket");
#endif
	  close(http);
	  close(https);
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
#endif

	  if ((passwdbuf = file_to_buf(passwd)) == NULL)
	    {
	      my_error(__FILE__, __LINE__, "cannot load file %s", passwd);
	      exit(ERR_FILE_READ);
	    }


	  if (parse_users(&users, passwdbuf))
	    {
	      exit(ERR_FILE_PARSE);
	    }

	  free(passwdbuf);


#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "starting HTTP request processing");
#endif

	  ret = process_request(&users, doc, doctitle, new_http, new_https);

#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "HTTP request processed (%d)", ret);
#endif

#ifndef ITERATIVE
	  exit(ret);
	}
      /* End of child code */
#endif

      if (new_http > 0)
	close(new_http);
      if (new_https > 0)
	close(new_https);
    }
  return 0; /* never reached */
}
