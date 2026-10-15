#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>


#define LOG_PATH "/tmp"
#define CGI_PATH "/tmp/cgi-bin"
#define DOC_PATH "/tmp/html"

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

  fwrite(buffer, 1, strlen(buffer), log);
  fflush(log);

  if (strncmp(buffer, "GET ", strlen("GET ")))
    {
      fprintf(stderr, "Malformed request %s", buffer);
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
      
      printf("<html>\n");
      printf("  <head><title>");
      printf(cgibin);
      printf("</title></head>\n");
      printf("  <body>\n");
      printf("    <pre>\n");
      system(cgiexe);
      printf("    </pre>\n");
      printf("  </body>\n"); 
      printf("</html>\n"); 
      fflush(stdout);
    }
  else 
    {
      snprintf(docpath, 512, "%s/%s", DOC_PATH, url);

      docfile= fopen(docpath, "r");

      if (docfile == NULL)
	{
	  printf("HTTP/1.0 404 File not found\n");
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
  struct stat fileinfo;
  char command[512];
  char docname[512];
  FILE *docfile;
  struct sockaddr_in server_addr;
  struct sockaddr_in client_addr;
  int sockfd, newsockfd, client_len, server_len;
  int port;

  if (argv[1] != NULL)
    {
      port = atoi(argv[1]);
    }
  else
    {
      port = 7979;
    }
  
  if (stat(CGI_PATH, &fileinfo))
    {
      snprintf(command, 512, "mkdir %s\n", CGI_PATH);
      system(command);
      snprintf(command, 512, "cp `which netstat` %s\n", CGI_PATH);
      system(command);
      snprintf(command, 512, "cp `which who` %s\n", CGI_PATH);
      system(command);
      snprintf(command, 512, "cp `which uptime` %s\n", CGI_PATH);
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
      fprintf(docfile, "\
<html>\n\
  <head><title>The Buggy Web Server (tm)</title></head>\n\
  <body>\n\
    <h1>Welcome to the Buggy Web Server (tm)</h1>\n\
    <p>This is the default page for the Buggy Web Server (tm)</p>\n\
  </body>\n\
</html>\n");
      fclose(docfile);
    }

  bzero((char *) &server_addr, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);
  server_addr.sin_addr.s_addr = INADDR_ANY;

  fprintf(stderr, "%s: using address %s and port %d\n",
	  argv[0],
	  inet_ntoa(server_addr.sin_addr),
	  port);

  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd == -1) 
    {
      perror("socket");
      exit(1);
    }

  server_len = sizeof(server_addr);
  if (bind(sockfd, (struct sockaddr *)&server_addr, server_len)) 
    {
      perror("bind");
      exit(1);
    }

  if (listen(sockfd, 5)) 
    {
      perror("listen");
      exit(1);
    }

  client_len = sizeof(client_addr);
  while (1)
    {
      newsockfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_len);
      if (newsockfd < 0) 
	{
	  perror("accept");
	  exit(1);
	}
  
      close(0);
      close(1);
      close(2);
      
      dup(newsockfd);
      dup(newsockfd);
      dup(newsockfd);
      close(newsockfd);
      manage_request((u_long) (client_addr.sin_addr.s_addr), 
		     (u_short) (client_addr.sin_port));
      shutdown(0, 2);
      
    }
  exit(0);
}



