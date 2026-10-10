#include <stdio.h>
#define _XOPEN_SOURCE
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <setjmp.h>
#include <pwd.h>
#include <fcntl.h>

#ifdef HAVE_LIBCRYPT
#include <crypt.h>
#endif

extern int h_errno;
#define JMPRET 5
int debug = 0;

#ifndef MAXHOSTNAMELEN
#define MAXHOSTNAMELEN 256
#endif
#define DEFAULT_PORT 10080
#define DOC_INDEX "\
      <p>Welcome to Re-Tard, the Bass Tard Corporation               \n \
      administration tool!</p>                                       \n	\
      <p>You can perform a number of useful tests on your system:</p>\n \
      <ul>                                                           \n	\
        <li><a href=\"cgi-bin/netstat\">Show the status of network   \n	\
        connections</a></li>                                         \n	\
        <li><a href=\"cgi-bin/who\">Display who is on          	     \n	\
        the system</a></li>					     \n	\
        <li><a href=\"cgi-bin/uptime\">Show how long the system      \n \
        has been running</a></li>				     \n \
        <li><a href=\"cgi-bin/ps\">Show the process status</a></li>  \n \
        <li><a href=\"cgi-bin/ifconfig\">Show the status of	     \n \
        network interfaces</a></li>				     \n \
        <li><a href=\"cgi-bin/lsof\">List the open files</a></li>    \n \
        <li><a href=\"cgi-bin/id\">Show the user under which the     \n	\
        server is running</a></li>				     \n \
      </ul>							     \n \
      <p>You can also notify the administrator of issues regarding   \n \
      the network status using the form below.</p>		     \n \
      <form action=\"/annote\" method=\"get\">	                     \n	\
      <p>User: <input type=\"text\" name=\"user\"></p>               \n \
      <p>Email: <input type=\"text\" name=\"email\"></p>             \n \
      <p>Note: <input type=\"textarea\" name=\"note\"></p>           \n \
      <input type=\"submit\" value=\"Send\"></p>                     \n	\
      </form>"
 
#define DOC_START "\
<?xml version=\"1.0\" encoding=\"utf-8\"?>				\
<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"	\
\"DTD/xhtml1-transitional.dtd\">					\
<html>									\
  <head>								\
    <title>The Bass Retard Administration Interface</title>		\
    <meta name=\"Author\" content=\"Massimo Zanardi\">			\
    <link href=\"/basstard.css\" rel=\"stylesheet\" type=\"text/css\">	\
  </head>								\
  <body>								\
    <div class=\"main\">						\
      <div class=\"header\">						\
        <h1>The Bass Retard Administration Interface</h1>		\
      </div>								\
      <div class=\"content\">"

#define DOC_END "\
      </div>								\
    </div>								\
    <div class=\"footer\">						\
      (C) 2005, The Bass Tard Corporation				\
    </div>								\
  </body>								\
</html>"

char logentry[256] = {0};

#define BASE_PATH "/tmp/bassretard" 
#define LOG_PATH "log"
#define CGI_PATH "cgi-bin"
#define DOC_PATH "html"
#define NOTE_PATH "notes"
#define CSS_FILE "basstard.css"
#define EXTRA_PATH "PATH=${PATH}:/sbin:/usr/sbin"
#define SHARED_PATH "/usr/local/share/bassretard/"

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
   
}


static int doDaemonize() {
  int fd;
  
  switch (fork()) {
  case -1: 
    return 0;
  case 0:
    break;
  default:
    exit(0);
  }
  
  if (setsid() == -1) {
    return 0;
  }
 
  //chdir("/");
  
  if ((fd = open("/dev/null", O_RDWR, 0)) != -1) {
    dup2(fd, STDIN_FILENO);
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);
    if (fd > 2)
      close (fd);
  } 
  else {
    return 0;
  }
  
  return 1;
}



int save_annotation(jmp_buf *e, char* user, char* email, char* note)
{
  FILE *userfd = NULL;
  char command [512];
  char userfile[1024];
  struct stat fileinfo;

  /* Verifies the email address */
  if (strchr(email, '.') == NULL)
    {
      longjmp(*e, JMPRET);
    }

  sprintf(userfile, "%s/%s", NOTE_PATH, user);

  if (stat(userfile, &fileinfo))
    {
      sprintf(command, "touch %s", userfile);
      system(command);
      if (stat(userfile, &fileinfo))
	{
	  printf("cannot create user annotation file %s\n", userfile);
	  fflush(stdout);
	  longjmp(*e, JMPRET);
	}
    }
  else
    {
      printf("<p>The last annotation submitted by the user was:</p>\n");
      printf("<pre>\n");
      fflush(stdout);
      sprintf(command, "tail -n 1 %s", userfile);
      system(command);
      printf("\n</pre>\n");
      fflush(stdout);
    }

  userfd = fopen(userfile, "a");
  if (userfd == NULL)
    {
      longjmp(*e, JMPRET);
    }
  fprintf(userfd, "NOTE: %s\n", note);
  fclose(userfd);

  return 0;
}

int parse_annotation(jmp_buf *env, char* command)
{
  char *p;
  char *user;
  char *email;
  char *note;

  if (debug) fprintf(stderr, "Parsing annotation: %s\n", command);
  /* Command is in the format: ?user=<username>&email=<email>&note=<note>*/
  p = memchr(command, '?', strlen(command));
  if (p == NULL)
    {
      fprintf(stderr, "Wrong format\n");
      return -1;
    }
  user = p + strlen("user=") + 1;
  p = memchr(user, '&', strlen(user));
  if (p == NULL)
    {
      fprintf(stderr, "Missing user in annotation\n");
      return -1;
    }
  *p = '\0';
  email = p + strlen("email=") + 1;
  p = memchr(email, '&', strlen(email));
  if (p == NULL)
    {
      fprintf(stderr, "Missing email in annotation\n");
      return -1;
    }
  *p = '\0';
  note = p + strlen("note=") + 1;

  if (debug) fprintf(stderr, "Saving note: %s, %s, %s\n", user, email, note);
  if (save_annotation(env, user, email, note) < 0)
    return -1;

  return 0;
}

void process_annotation(char *parameters)
{
  jmp_buf env;
  char buffer[256];
  int i = 0;
  
  printf(DOC_START);
  fflush(stdout);
  i = setjmp(env);
  if (i == JMPRET)
    {
      printf("<p>Cannot create an annotation. Invalid parameters.</p>\n");
      printf(DOC_END);
      fflush(stdout);
      return;
    }

  strcpy(buffer, parameters);
  if (parse_annotation(&env, buffer) < 0)
    {
      printf("<p>ERROR: There was an error saving the annotation.</p>\n");
    }
  else
    {
      printf("<p>Annotation saved!</p>\n");
    }
  fflush(stdout);
  printf(DOC_END);
  fflush(stdout);

  return;
}

char *
getline_nocrlf(int fd)
{
  char line[1024];
  char *str = NULL;
  int ret = 0;
  int line_size = 0;
  int index = 0;
  int i = 0;
  char c = 0;
  
  line_size = 1024;
  index = 0;
  c = '\0';

  while (c != '\n')
    {
      ret = read(fd, &c, 1);
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
  
      line[index] = c;
      index++;
      line[index] = '\0';
    }
      
  for (i = index - 1; i >= 0; i--)
    {
      if ((line[i] != '\n') && (line[i] != '\r')) break;
      
      line[i] = '\0';
    }

  str = strdup(line);
  return str;
}

void manage_request(u_long client_addr, u_short client_port)
{
  char buffer[512];
  int i, numc;
  FILE *log;
  char docbuffer[512];
  static char docpath[512], *logfile;
  FILE *docfile;
  char cgiexe[512];
  char *proto;
  char *url;
  char *cgibin;
  struct in_addr client_addr_in;
  char *line;

  i = 0;
  while((numc = read(0, &(buffer[i]), 1)) == 1)
    {
      if (buffer[i] == '\n')
	{
	  if (buffer[i - 1] == '\r') buffer[i - 1] = '\0';
	  else buffer[i] = '\0';
	  break;
	}
      i++;
    }

  if (numc == 0)
    {
      perror("read");
      return;
    }

  /* Reads the rest of the headers */
  while(1)
    {
      line = getline_nocrlf(0);
      if (line == NULL) break;
      if (strlen(line) == 0) 
	{
	  free(line);
	  break;
	}
      free(line);
    }
  
  client_addr_in.s_addr = client_addr;

  logfile = malloc(512);
  snprintf(logfile, 512, "%s/%s_%d", 
	   LOG_PATH,
	   inet_ntoa(client_addr_in), 
	   htons(client_port));

  log = fopen(logfile, "a+");
  if (log == NULL)
    {
      fprintf(stderr, "Cannot open log file %s\n", logfile);
      return;
    }

  sprintf(logentry, "LOG: %s", buffer);
  fwrite(logentry, 1, strlen(logentry), log);
  fflush(log);

  printf("HTTP/1.0 200\r\n");
  printf("Content-Type: text/html\r\n\r\n");
  fflush(stdout);

  if (strncmp(buffer, "GET ", strlen("GET ")))
    {
      fprintf(stderr, "Malformed request \"%s\"\n", buffer);
    }
  proto = strstr(buffer, " HTTP/1.0");
  if (proto != NULL)
    {
      *proto = '\0';
    }
  else
    {
      proto = strstr(buffer, " HTTP/1.1");
      if (proto != NULL)
	{
	  *proto = '\0';
	}
    }
  url = buffer + strlen("GET ");
  if (!strncmp(url, "/cgi-bin/", strlen("/cgi-bin/")))
    {
      cgibin = url + strlen("/cgi-bin/");
      snprintf(cgiexe, 512, "%s/%s", CGI_PATH, cgibin);
      if (!strcmp(cgibin, "ps"))
	{
	  strcat(cgiexe, " auxw");
	}
      printf(DOC_START);
      printf("\n<!--");
      printf(cgibin);
      printf("-->\n");
      printf("<pre>\n"); 
      fflush(stdout);
      system(cgiexe);
      printf("</pre>\n"); 
      printf(DOC_END);
      fflush(stdout);
    }
  else if (!strncmp(url, "/annote", strlen("/annote")))
    {
      process_annotation(url + strlen("/annote"));
    }
  else if ((strlen(url) == 1) && (url[0] == '/'))
    {
      sprintf(docpath, "%s/index.html", DOC_PATH);
      docfile= fopen(docpath, "r");

      if (docfile == NULL)
	{
	  printf("Cannot find the file: \"");
	  printf(buffer);
	  printf("\" that you requested");

	  fflush(stdout);
	  return;
	}
      
      while (1)
	{
	  numc = fread(docbuffer, 1, 512, docfile);
	  fwrite(docbuffer, 1, numc, stdout);
	  fflush(stdout);

	  if (numc < 512) break;
	}
    }
  else 
    {
      sprintf(docpath, "%s/%s", DOC_PATH, url);

      docfile= fopen(docpath, "r");

      if (docfile == NULL)
	{
	  printf("Cannot find the file: \"");
	  printf(buffer);
	  printf("\" that you requested");

	  fflush(stdout);
	  return;
	}
      
      while (1)
	{
	  numc = fread(docbuffer, 1, 512, docfile);
	  fwrite(docbuffer, 1, numc, stdout);
	  fflush(stdout);

	  if (numc < 512) break;
	}
    }
  return;
}

int main(int argc, char *argv[]) 
{
  char homedir[1024];
  int port = DEFAULT_PORT;
  struct sockaddr_in client_addr;
  char command[512];
  char docname[512];
  int pid;
  int i = 0;
  int on = 1;
  int daemon = 0;
  struct stat fileinfo;
  char *css_filename = NULL;
  FILE *css_file = NULL;
  int css_filesize = 0;
  char *css_buf = NULL;
  int css_ret;
  FILE *docfile;
  struct sockaddr_in server_addr;
  int sockfd, newsockfd, client_len;

  /* Parses the command line arguments */
  homedir[0] = '\0';
  i = 1;
  while (i < argc)
    {
      if (!strcmp(argv[i], "--port"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    fprintf(stderr, "missing argument of parameter \"%s\"\n", argv[i - 1]);
	    exit(1);
	  }
	  
	  port = (int)strtoul(argv[i], (char **)NULL, 10);
	}
      else if (!strcmp(argv[i], "--homedir"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    fprintf(stderr, "missing argument of parameter \"%s\"\n", argv[i - 1]);
	    exit(1);
	  }
  
	  strncpy(homedir, argv[i], sizeof(homedir));
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
      else if (!strcmp(argv[i], "--css"))
	{
	  i++;
	  if (argv[i] == NULL) { 
	    fprintf(stderr, "missing argument of parameter \"%s\"\n", argv[i - 1]);
	    exit(1);
	  }
	  
	  css_filename = argv[i];
	}

      else
	{
	  fprintf(stderr, "unknown parameter \"%s\"\n", argv[i]);
	  exit(1);
	}
      i++;
    }

  if (strlen(homedir) == 0)
    {
      strcpy(homedir, BASE_PATH);
    }
  if (css_filename == NULL) {
    css_filename = SHARED_PATH CSS_FILE;
  }
  
  css_file = fopen(css_filename, "r");
  if (css_file == NULL)
    {
      fprintf(stderr, "missing CSS file.\n");
      exit(1);
    }
  if (fseek(css_file, 0, SEEK_END) < 0)
    {
      fprintf(stderr, "cannot seek CSS file\n");
      exit(1);
    }
    
  css_filesize = ftell(css_file);

  if (css_filesize < 0)
    {
      fprintf(stderr, "cannot determine the size of CSS file\n");
      exit(1);
    }

  css_buf = (char *)malloc(css_filesize + 1);
  if (css_buf == NULL)
    {
      fprintf(stderr, "not enough memory to hold CSS file\n");
      exit(1);
    }

  fseek(css_file, 0, SEEK_SET);
  css_ret = fread(css_buf, 1, css_filesize, css_file);

  if (css_ret < css_filesize)
    {
      fprintf(stderr, 
	     "read failed and returned %d when reading file of size %d\n", 
	     css_ret, css_filesize);
      exit(1);
    }
  fclose(css_file);
  css_buf[css_filesize] = '\0';

  if (stat(homedir, &fileinfo))
    {
      snprintf(command, 512, "mkdir -m 700 %s\n", homedir);
      system(command);
    }

  if (stat(homedir, &fileinfo))
    {
      fprintf(stderr, "cannot create %s\n", homedir);
      exit(1);
    }

  if (chdir(homedir))
    {
      fprintf(stderr, "cannot change directory to %s\n", homedir);
      exit(1);
    }

  if (stat(CGI_PATH, &fileinfo))
    {
      snprintf(command, 512, "mkdir -m 700 %s\n", CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which netstat` %s\n", EXTRA_PATH, CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which who` %s\n",EXTRA_PATH, CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which uptime` %s\n",EXTRA_PATH, CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which ps` %s\n",EXTRA_PATH, CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which ifconfig` %s\n",EXTRA_PATH, CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which lsof` %s\n",EXTRA_PATH, CGI_PATH);
      system(command);
      snprintf(command, 512, "%s cp `which id` %s\n",EXTRA_PATH, CGI_PATH);
      system(command);
    }

  if (stat(DOC_PATH, &fileinfo))
    {
      snprintf(command, 512, "mkdir %s\n", DOC_PATH);
      system(command);
      snprintf(docname, 512, "%s/index.html", DOC_PATH);
      docfile = fopen(docname, "w+");
      if (docfile == NULL)
	{
	  fprintf(stderr, "Cannot create index.html file\n");
	  exit(1);
	}
      fprintf(docfile, DOC_START);
      fprintf(docfile, DOC_INDEX);
      fprintf(docfile, DOC_END);
      fclose(docfile);

      snprintf(docname, 512, "%s/%s", DOC_PATH, CSS_FILE);
      docfile = fopen(docname, "w+");
      if (docfile == NULL)
	{
	  fprintf(stderr, "Cannot create CSS file\n");
	  exit(1);
	}
      fprintf(docfile, "%s", css_buf);
      fclose(docfile);
    }

  if (stat(LOG_PATH, &fileinfo))
    {
      snprintf(command, 512, "mkdir %s\n", LOG_PATH);
      system(command);
    }

  if (stat(NOTE_PATH, &fileinfo))
    {
      snprintf(command, 512, "mkdir %s\n", NOTE_PATH);
      system(command);
    }

  bzero((char *) &server_addr, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);
  server_addr.sin_addr.s_addr = INADDR_ANY;

  sockfd = socket(PF_INET, SOCK_STREAM, 0);
  if (sockfd == -1) 
    {
      perror("socket");
      exit(1);
    }

  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char *)&on, sizeof(on)) == -1) 
    {
      perror("setsockopt");
      exit(1);
    }

  if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr))) 
    {
      perror("bind");
      exit(1);
    }

  if (listen(sockfd, 5)) 
    {
      perror("listen");
      exit(1);
    }

  if (debug) fprintf(stderr, "using address %s and port %d\n",
		     inet_ntoa(server_addr.sin_addr),
		     port);
  
  if(daemon && !doDaemonize()) {
    fprintf(stderr, "Error, cannot daemonize\n");
    exit(1);
  }
  
  (void) signal(SIGCHLD, reaper);
 
  client_len = sizeof(client_addr);
  while (1)
    {
      newsockfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_len);
      if (newsockfd < 0) 
	{
	  perror("accept");
	  exit(1);
	}

      pid = fork();
      
      if (pid == 0)
	{  
	  dup2(newsockfd, STDIN_FILENO);
	  dup2(newsockfd, STDOUT_FILENO);
	  dup2(newsockfd, STDERR_FILENO);
	  if (newsockfd > 2)
	    close (newsockfd);

	  
	  manage_request((u_long) (client_addr.sin_addr.s_addr), 
			 (u_short) (client_addr.sin_port));
	  
	  close(0);
	  close(1);
	  close(2);
	  
	  exit(0);
	}
      /* shutdown(newsockfd, 2); */
      close(newsockfd); 
    }
  
  return 0;
}



