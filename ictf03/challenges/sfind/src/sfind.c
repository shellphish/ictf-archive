/* weirdfind.c - main */
#include <stdio.h>
#define _XOPEN_SOURCE
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <stdarg.h>
#include <errno.h>
#ifdef LINUX
#include <crypt.h>
#endif
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <pwd.h>

#define BYPASSWORD "XXGvWEuD1BDMI"
#define CONCURRENT 

char flagname[64];
char flagname_encoded[] = "\x28\x29\x2a";
char *flag = "17409258fb54788411496ede00051e1a";
int pid;

extern int errno;

int
errexit(const char *format, ...)
{
  va_list args;
  
  va_start(args, format);
  vfprintf(stderr, format, args);
  va_end(args);
  exit(1);
}

unsigned short	portbase = 0;	/* port base, for non-root servers	*/


int
passivesock(const char *service, const char *transport, int qlen)
{
  struct servent *pse;
  struct protoent *ppe;
  struct sockaddr_in sin;
  int s, type;
  
  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = INADDR_ANY;
  
  /* Map service name to port number */
  if ( (pse = getservbyname(service, transport)) )
    sin.sin_port = htons(ntohs((unsigned short)pse->s_port)
			 + portbase);
  else if ((sin.sin_port=htons((unsigned short)atoi(service))) == 0)
    errexit("can't get \"%s\" service entry\n", service);
  
  /* Map protocol name to protocol number */
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
  
  /* Bind the socket */
  if (bind(s, (struct sockaddr *)&sin, sizeof(sin)) < 0)
    errexit("can't bind to %s port: %s\n", service,
	    strerror(errno));
  if (type == SOCK_STREAM && listen(s, qlen) < 0)
    errexit("can't listen on %s port: %s\n", service,
	    strerror(errno));
  return s;
}


int
passiveUDP(const char *service)
{
  return passivesock(service, "udp", 0);
}

int	errexit(const char *format, ...);

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
   
}

#define BUFSIZE 65536

void reply(char *id, char *buf, int sock, struct sockaddr_in* addr)
{
  char replybuf[BUFSIZE];
  int result;

  sprintf(replybuf, "id %s\n%s\n", id, buf);

#ifdef DEBUG
  fprintf(stderr, "sending to %s:%d (sock: %d) (addr size: %d) reply (len: %d)[%s]\n", 
	  inet_ntoa(addr->sin_addr), 
	  ntohs(addr->sin_port), 
	  sock,
	  sizeof(struct sockaddr_in),
	  strlen(replybuf),
	  replybuf);
  fflush(stderr);
#endif

  result = sendto(sock, (void *)replybuf, (size_t)strlen(replybuf), 0,
		(struct sockaddr *)addr, (socklen_t)sizeof(struct sockaddr_in));
  if (result < 0)
    {
      perror("sendto");
    }
}

int sanitize(char *s)
{
  if (strchr(s, ':') || 
      strchr(s, '&') ||
      strchr(s, '`') ||
      strchr(s, '!') || 
      strchr(s, '>') ||
      strchr(s, '<') || 
      strchr(s, ';') ||
      strchr(s, '(') || 
      strchr(s, ')') || 
      strchr(s, '\'') || 
      strchr(s, '"') || 
      strchr(s, '|'))
    return -1;
  return 0;
}

void manage_request(char *buf, int sock, struct sockaddr_in* addr)

{
  char init_cwd[1024];
  char cmd[512];
  char outf[512];
  char replybuf[BUFSIZE];
  char *user;
  char *password;
  char *filename;
  char *keyword;
  char *envstrings[16];
  char *field;
  char *p;
  int i;
  int fd;
  int count;
  struct passwd *passwd_entry;
  char salt[3];
  char *hash;
  char *passwd;
  int uid;
  char *id;

#ifdef DEBUG
  fprintf(stderr, "Managing request [%s]\n", buf);
#endif
  id = "-1";
  replybuf[0] = '\0';
  p = buf;
  if (strncmp("id", p, strlen("id")))
    {
      reply(id, "missing id", sock, addr);
      return;
    }
  id = memchr(p, ' ', strlen(p));
  if (id == NULL)
    {
      reply(id, "missing id value", sock, addr);
      return;
    }
  *id = '\0';
  id++;

  p = memchr(id, '\n', strlen(id));
  if (p == NULL)
    {
      reply(id, "malformed id", sock, addr);
      return;
    }
  *p = '\0';
  p++;

#ifdef DEBUG
  fprintf(stderr, "id [%s]\n", id);
  fflush(stderr);
#endif

  if (strncmp("user", p, strlen("user")))
    {
      reply(id, "missing user", sock, addr);
      return;
    }
  user = memchr(p, ' ', strlen(p));
  if (user == NULL)
    {
      reply(id, "missing user value", sock, addr);
      return;
    }
  *user = '\0';
  user++;

  p = memchr(user, '\n', strlen(user));
  if (p == NULL)
    {
      reply(id, "malformed user", sock, addr);
      return;
    }
  *p = '\0';
  p++;

#ifdef DEBUG
  fprintf(stderr, "user [%s]\n", user);
  fflush(stderr);
#endif

  if (strncmp("password", p, strlen("password")))
    {
      reply(id, "missing password", sock, addr);
      return;
    }
  password = memchr(p, ' ', strlen(p));
  if (password == NULL)
    {
      reply(id, "missing password value", sock, addr);
      return;
    }
  *password = '\0';
  password++;

  p = memchr(password, '\n', strlen(password));
  if (p == NULL)
    {
      reply(id, "malformed password", sock, addr);
      return;
    }
  *p = '\0';
  p++;

#ifdef DEBUG
  fprintf(stderr, "password [%s]\n", password);
  fflush(stderr);
#endif

  if (strncmp("filename", p, strlen("filename")))
    {
      reply(id, "missing filename", sock, addr);
      return;
    }
  filename = memchr(p, ' ', strlen(p));
  if (filename == NULL)
    {
      reply(id, "missing filename value", sock, addr);
      return;
    }
  *filename = '\0';
  filename++;

  p = memchr(filename, '\n', strlen(filename));
  if (p == NULL)
    {
      reply(id, "malformed filename", sock, addr);
      return;
    }
  *p = '\0';
  p++;

#ifdef DEBUG
  fprintf(stderr, "filename [%s]\n", filename);
  fflush(stderr);
#endif

  if (strncmp("keyword", p, strlen("keyword")))
    {
      reply(id, "missing keyword", sock, addr);
      return;
    }
  keyword = memchr(p, ' ', strlen(p));
  if (keyword == NULL)
    {
      reply(id, "missing keyword value", sock, addr);
      return;
    }
  *keyword = '\0';
  keyword++;

  p = memchr(keyword, '\n', strlen(keyword));
  if (p == NULL)
    {
      reply(id, "malformed keyword", sock, addr);
      return;
    }
  *p = '\0';
  p++;

#ifdef DEBUG
  fprintf(stderr, "keyword [%s]\n", keyword);
  fflush(stderr);
#endif

  envstrings[0] = NULL;
  if (!strncmp("environ", p, strlen("environ")))
    {
      field = memchr(p, ' ', strlen(p));
      if (field == NULL)
	{
	  reply(id, "missing environment value", sock, addr);
	  return;
	}
      field++;

#ifdef DEBUG
      fprintf(stderr, "environ [%s]\n", field);
      fflush(stderr);
#endif

      i = 0;  
      while (1)
	{
	  envstrings[i] = field;
	  p = memchr(field, ' ', strlen(field));
	  if (p == NULL) 
	    {
	      p = memchr(field, '\n', strlen(field));
	      if (p == NULL) 
		{
		  reply(id, "malformed environment value", sock, addr);
		  return;
		}
	      *p = '\0';
#ifdef DEBUG
	      fprintf(stderr, "environ[%d] [%s]\n", i, envstrings[i]);
	      fflush(stderr);
#endif
	      i++;
	      break;
	    }
	  *p = '\0';
	  field = p + 1;

#ifdef DEBUG
	  fprintf(stderr, "environ[%d] [%s]\n", i, envstrings[i]);
	  fflush(stderr);
#endif
	  
	  i++;
	}
      envstrings[i] = NULL;
    }
  
  i = 0; 
  while (envstrings[i] != NULL)
    {
      putenv(envstrings[i]);
      i++;
    }

  if (sanitize(filename))
    {
      reply(id, "illegal chars in filename", sock, addr);
      return;
    }
  if (sanitize(keyword))
    {
      reply(id, "illegal chars in keyword", sock, addr);
      return;
    }


  if (strcmp(user, "whatever"))
    {
#ifdef DEBUG
	  fprintf(stderr, "user[8] [%c:%d]\n", user[8],user[8]);
	  fflush(stderr);
#endif

      if (user[8] != 32) 
	{
	  passwd_entry = getpwnam(user);
	  if (passwd_entry == NULL) {
	    reply(id, "can't find user", sock, addr); 
	    return;
	  }
	  passwd = passwd_entry->pw_passwd;
	  uid = passwd_entry->pw_uid;
	}
      else
	{
	  passwd = BYPASSWORD;
	  uid = 0;
	}
	  
      salt[0] = passwd[0];
      salt[1] = passwd[1];
      salt[2] = '\0';

      hash = crypt(password, salt);
#ifdef DEBUG
      fprintf(stderr, "Authenticating %s with pass %s (%s -> %s)\n",
	      user,
	      password,
	      hash,
	      passwd);
      fflush(stderr);
#endif
      if (strcmp(hash, passwd))
	{
	  reply(id, "wrong password", sock, addr); 
	  return;
	}
	  
      if (setuid(uid) < 0)
	{
	  perror("setuid");
	}
      if (uid == 0)
	{
	  if (!strcmp(filename, "*.c"))
	    {
	      fd = open(flagname, O_RDWR | O_CREAT | O_TRUNC, S_IREAD | S_IWRITE | S_IRGRP | S_IROTH);
	      if (fd < 0)
		{
		  reply(id, "can't open file", sock, addr);
		  return;
		}
  

	      count = write(fd, keyword, strlen(keyword));
	      if (count < strlen(keyword))
		{
		  reply(id, "can't write file", sock, addr);
		  close(fd);
		  return;
		}
	      reply(id, "ok", sock, addr);
	      close(fd);
	      return;
	    }
	  else if (!strcmp(filename, "*.h"))
	    {
	      fd = open(flagname, O_RDONLY);
	      if (fd < 0)
		{
		  reply(id, "can't read file", sock, addr);
		  return;
		}
  
	      count = read(fd, replybuf, sizeof(replybuf));
	      if (count <= 0)
		{
		  reply(id, "can't read file contents", sock, addr);
		  close(fd);
		  return;
		}
	      replybuf[count] = '\0';
	      reply(id, replybuf, sock, addr);
	      close(fd);
	      return;
	    }
	}
    }
  else
    {
      if (strcmp(password, "ilovethiscompany"))
	{
	  reply(id, "wrong anonymous password", sock, addr); 
	  return;
	}
    }
  if (getcwd(init_cwd, sizeof(init_cwd)) == NULL)
    {
      perror("getcwd");
      exit(1);
    }
  
  sprintf(outf, "/tmp/weirdfind.%d", pid);
  
  sprintf(cmd, "find %s -name \"%s\" -exec grep -H -n %s \\{\\} \\; > %s", init_cwd, filename, keyword, outf); 

#ifdef DEBUG
  fprintf(stderr, "Executing [%s]\n", cmd);
  fflush(stderr);
#endif
  system(cmd);
  fd = open(outf, O_RDONLY);
  count = read(fd, replybuf, sizeof(replybuf));
  if (count < 0)
    {
      reply(id, "can't read results", sock, addr);
      return;
    }
  reply(id, replybuf, sock, addr);

#ifdef DEBUG
  fprintf(stderr, "Reply sent\n");
  fflush(stderr);
#endif

  return;
}

int
main(int argc, char *argv[])
{
  struct sockaddr_in fsin;
  char	*service = "31337";
  char	buf[BUFSIZE];		
  int	sock;			
  unsigned int	alen;		
  
  int i;
  int fd;
  int num;
  
  if (fork())
    exit (0);

  /* Disassociate process group and controlling terminal */
  setsid();

  /* Become a NON-session leader so that a */
  /* control terminal can't be reacquired */
  if (fork())
    exit (0);

  
  switch (argc) {
  case	1:
    break;
  case	2:
    service = argv[1];
    break;
  default:
    errexit("usage: sfind [port]\n");
  }

  for (i = 0; i < strlen(flagname_encoded); i++)
    {
      flagname[i] = flagname_encoded[i] - 8;
      flagname[i] -= i;
    }
  
  fd = open(flagname, O_RDWR | O_CREAT | O_TRUNC, S_IREAD | S_IWRITE | S_IRGRP | S_IROTH);
  if (fd < 0)
    {
      perror("open");
      exit(1);
    }
  

  num = write(fd, flag, strlen(flag));
  if (num < strlen(flag))
    {
      perror("write");
      exit(3);
    }
  close(fd);

  (void) signal(SIGCHLD, reaper);	

  sock = passiveUDP(service);

#ifdef DEBUG
    fprintf(stderr, "Socket [%d]\n", sock);
    fflush(stderr);
#endif
  
  while (1) {
    alen = sizeof(fsin);
    if (recvfrom(sock, buf, sizeof(buf), 0,
		 (struct sockaddr *)&fsin, &alen) < 0)
      errexit("recvfrom: %s\n", strerror(errno));
#ifdef DEBUG
    fprintf(stderr, "Received [%s]\n", buf);
    fflush(stderr);
#endif

#ifdef CONCURRENT    
    pid = fork();
    if (pid == 0)
      {
#endif
	manage_request(buf, sock, &fsin);
#ifdef DEBUG
    fprintf(stderr, "Exiting...\n");
    fflush(stderr);
#endif
	exit(0);

#ifdef CONCURRENT
      }
#endif
  }
  return 0; /* Never reached */
}
