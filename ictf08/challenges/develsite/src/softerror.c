#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <unistd.h>
#include <ctype.h>
#include <pwd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <netdb.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/mman.h>

#ifndef	INADDR_NONE
#define	INADDR_NONE	0xffffffff
#endif	/* INADDR_NONE */

#define DEBUG
#define BUFSIZE 512

int debug = 0;
int devel1_uid = 0;
int devel1_gid = 0;
char* devel1_dir = NULL;
int devel2_uid = 0;
int devel2_gid = 0;
char* devel2_dir = NULL;
char *buf = NULL;

#if HAVE_STDARG_H
#  include <stdarg.h>
#  define VA_START(a, f)        va_start(a, f)
#else
#  if HAVE_VARARGS_H
#    include <varargs.h>
#    define VA_START(a, f)      va_start(a)
#  endif
#endif
#ifndef VA_START
#  error no variadic api
#endif

  /* Define these two macros to check the effect of missing 
     vprintf and _doprnt

     #define HAVE_VPRINTF 0
     #define HAVE_DOPRNT 0 */

#if HAVE_VPRINTF
#  define VFPRINTF(file, fmt, ap)        vfprintf(file, fmt, ap)
#else
#  if HAVE_DOPRNT
#    define VFPRINTF(file, fmt, ap)      _doprnt(fmt, ap, file)
#  else
#    error no vfprintf or _doprnt
#  endif
#endif

#include "mydiag.h"

void
#if HAVE_STDARG_H
my_error (char *file, int line, const char *format, ...)
#else
my_error (file, line, format, va_alist)
     char *file;
     int line;
     const char *format;
     va_dcl
#endif
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stderr, "%s:%d: ERROR: ", file, line);
  (void)VFPRINTF(stderr, format, ap);
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stderr);
    }

  fflush(stderr);
  return;
}

void
#if HAVE_STDARG_H
my_warning (char *file, int line, const char *format, ...)
#else
my_warning (file, line, format, va_alist)
     char *file;
     int line;
     const char *format;
     va_dcl
#endif
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stderr, "%s:%d: WARNING: ", file, line);
  (void)VFPRINTF(stderr, format, ap);
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stderr);
    }

  fflush(stderr);
  return;
}

void
#if HAVE_STDARG_H
my_debug (char *file, int line, const char *format, ...)
#else
my_debug (file, line, format, va_alist)
     char *file;
     int line;
     const char *format;
     va_dcl
#endif
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stderr, "%s:%d: DEBUG: ", file, line);
  (void)VFPRINTF(stderr, format, ap); 
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stderr);
    }

  fflush(stderr);
  return;
}

void
#if HAVE_STDARG_H
my_message (char *file, int line, const char *format, ...)
#else
my_message (file, line, format, va_alist)
     char *file;
     int line;
     const char *format;
     va_dcl
#endif
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stdout, "%s:%d: MESSAGE: ", file, line);
  (void)VFPRINTF(stdout, format, ap); 
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stdout);
    }

  fflush(stdout);
  return;
}


void reaper(int sig)
{
  int status;

  if (debug > 1) {
    my_debug(__FILE__, __LINE__, "SIGCHLD handler: start\n");
  }
  while (waitpid(-1, &status, WNOHANG) > 0);
  if (debug > 1){
    my_debug(__FILE__, __LINE__, "SIGCHLD handler: child exited with status %d\n", status);
  }
  return;
}

extern unsigned int get_sp(void);
extern unsigned int get_fp(void);

int manage_client(int s)
{
  int choice;
  int c;
  char local_buf[BUFSIZE];
  FILE *f;
#define TASKFILE "tasks.txt"

  dup2(s, 0);
  dup2(s, 1);
  dup2(s, 2);

  while (1) {
    fprintf(stdout, "Please select your choice:\n\t1) See the current tasks\n\t2) Add a task to the list\n\t3) Work as Developer 1\n\t4) Work as Developer 2\nYour choice: "); 
    fflush(stdout);
    fgets(buf, BUFSIZE, stdin);
    choice = atoi(buf);
    switch(choice) {
    case 1:
      f = fopen(TASKFILE, "r");
      if (f == NULL) {
	fprintf(stderr, "There is no task file!\n");
	continue;
      }
      while (1) {
	c = fread(buf, 1, BUFSIZE, f);
	fwrite(buf, 1, c, stdout);
	if (c < BUFSIZE) break;
      }
      printf("\n");
      fclose(f);
      break;
    case 2:
      fprintf(stdout, "Insert your task:\n");
      fflush(stdout);
      fgets(buf, BUFSIZE, stdin);
      memcpy(local_buf, buf, BUFSIZE);
      f = fopen(TASKFILE, "a");
      if (f == NULL) {
	fprintf(stderr, "Cannot open the task file!\n");
	break;
      }
      mprotect(buf, 0x1000, PROT_READ);
      fprintf(f, buf);
      mprotect(buf, 0x1000, PROT_READ | PROT_WRITE);
      fprintf(f, "\n");
      fclose(f);
      break;
    case 3:
      chdir(devel1_dir);
      setgid(devel1_gid);
      setuid(devel1_uid);
      execle("/bin/bash", "/bin/bash", "-i", (char *)0, NULL);
      break;
    case 4:
      chdir(devel2_dir);
      setgid(devel2_gid);
      setuid(devel2_uid);
      execle("/bin/bash", "/bin/bash", "-i", (char *)0, NULL);
      break;
    case 13:
      fprintf(stdout, "When reporting a bug, please include the following information:\n"
	      "Stack: %08x Frame: %08x Buffer: %p [%s]\n"
	      "devel1_uid: %p [%u]\n"
	      "devel1_gid: %p [%u]\n"
	      "devel2_uid: %p [%u]\n"
	      "devel2_gid: %p [%u]\n",
	      get_sp(), get_fp(), buf, buf,
	      &devel1_uid, devel1_uid,
	      &devel1_gid, devel1_gid,
	      &devel2_uid, devel2_uid,
	      &devel2_gid, devel2_gid);
      fflush(stdout);
      break;
    default:
      fprintf(stderr, "Wrong choice...\n");
      continue;
    }
  }
  return -1;
}

int 
main(int argc, char *argv[])
{
  struct sockaddr_in sin; 
  int s = 0, ns = 0; 
  int on = 1;
  int port = 1337;
  struct sockaddr_in client_addr;
  int client_addr_len = 0;
  int pid = 0;
  struct passwd *pwd;

  /* Sets the SIGCHILD handler */
  signal(SIGCHLD, reaper);

  if (geteuid() != 0) {
    my_error(__FILE__, __LINE__, "you have to be root\n");
    return -1;
  }

  pwd = getpwnam("devel1");
  if (pwd == NULL) {
    my_error(__FILE__, __LINE__, "You need to have a devel1 user\n");
    return -1;
  }
  devel1_uid = pwd->pw_uid;
  devel1_gid = pwd->pw_gid;
  devel1_dir = strdup(pwd->pw_dir);

  pwd = getpwnam("devel2");
  if (pwd == NULL) {
    my_error(__FILE__, __LINE__, "You need to have a devel2 user\n");
    return -1;
  }
  devel2_uid = pwd->pw_uid;
  devel2_gid = pwd->pw_gid;
  devel2_dir = strdup(pwd->pw_dir);

  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = INADDR_ANY;
  sin.sin_port = htons(port);

  /* Initialize buffer */
  if ((buf = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE,
	MAP_ANONYMOUS | MAP_PRIVATE, -1, 0)) == ((void *) -1)) {
	  fprintf(stderr, "ERROR: %s\n", strerror(errno));
	  my_error(__FILE__, __LINE__, "unable to map buffer\n");
	  return -1;
  }

  /* Allocate a socket */
  s = socket(PF_INET, SOCK_STREAM, 6);
  if (s < 0) {
    my_error(__FILE__, __LINE__, "can't create socket: %s\n", strerror(errno));
    return -1;
  }
  
  on = 1;
  if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &on, sizeof (int))) {
    my_error(__FILE__, __LINE__, "can't reuse address: %s\n", strerror(errno));
    return -1;
  }

  if (bind(s, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
    my_error(__FILE__, __LINE__, "can't bind to port: %s\n", strerror(errno));
    return -1;
  }

  if (listen(s, 5) < 0) {
    my_error(__FILE__, __LINE__, "can't listen on port: %s\n", strerror(errno));
    return -1;
  }

  while(1) {
    ns = accept(s, (struct sockaddr *)&client_addr, (socklen_t *)&client_addr_len);
    
    if (ns < 0)	{
      my_error(__FILE__, __LINE__, "accept() failed");
      return -1;
    }
    pid = fork();
    if (pid < 0) {
      my_error(__FILE__, __LINE__, "fork() failed");
      return -1;
    }
    /* Beginning of child code */
    if (pid == 0) {
      close(s);
      return manage_client(ns);
    }
    /* Parent code */
    close(ns);
  }

  return 0;
}

