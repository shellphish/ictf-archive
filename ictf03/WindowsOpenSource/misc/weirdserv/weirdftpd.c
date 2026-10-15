/* weirdftp */

#include <stdio.h>
#define _XOPEN_SOURCE
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#ifdef LINUX
#include <crypt.h>
#endif
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <pwd.h>

#define CONCURRENT
#define NOROOT

int other = 0;
int bypass = 0;
int dsock = 0;
int cport = 21;
int dport = 2020;
char *password = "ccglUuTOIlJ8g";
char filename[64];
char filename_encoded[] = "\x37\x7d\x77\x7b\x3b\x3b\x86\x40\x41\x3e\x87\x81\x7d\x8d";
char *flag = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";
char init_cwd[1024];

void reaper(int sig)
{
  int status;
  while (wait3(&status, WNOHANG, (struct rusage *)0) >= 0)
    {/* empty */}
   
}

void reply(int code, char *s) 
{
  if (s[0] == '-')
    {
      printf("%d%s\r\n", code, s);
    }
  else
    {
      printf("%d %s\r\n", code, s);
    }
  fflush(stdout);
}

/* FTP Command tokens */
enum command_types {USER,PASS,ACCT,CWD,CDUP,SMNT,REIN,QUIT,
      PORT,PASV,TYPE,STRU,MODE,RETR,STOR,STOU,APPE,ALLO,REST,RNFR,RNTO,
      ABOR,DELE,RMD,MKD,PWD,LIST,NLST,SITE,SYST,STAT,HELP,NOOP,EOFC,ERROR} ;

/* struct used to build a table mapping command character sequences to
   their command token listed above */
struct command_list {
  char *command ;
  enum command_types command_code ;
} ;

/* Lookup table for FTP Commands */
struct command_list command_lookup[] = {
  "USER", USER,  "PASS", PASS,  "ACCT", ACCT,  "CWD",  CWD,   "CDUP", CDUP,
  "SMNT", SMNT,  "REIN", REIN,  "QUIT", QUIT,  "PORT", PORT,  "PASV", PASV,
  "TYPE", TYPE,  "STRU", STRU,  "MODE", MODE,  "RETR", RETR,  "STOR", STOR,
  "STOU", STOU,  "APPE", APPE,  "ALLO", ALLO,  "REST", REST,  "RNFR", RNFR,
  "RNTO", RNTO,  "ABOR", ABOR,  "DELE", DELE,  "RMD",  RMD,   "MKD",  MKD,
  "PWD",  PWD,   "LIST", LIST,  "NLST", NLST,  "SITE", SITE,  "SYST", SYST,
  "STAT", STAT,  "HELP", HELP,  "NOOP", NOOP,  "EOFC", EOFC
} ;

/* Get a ftp command from the command stream, convert to command code and
   parse command argument */
enum command_types 
get_command(char *buf) 
{
  char cmd[16];
  int i,ch;
  int argexp = 0;

  i = 0;
  cmd[i] = '\0';
  while (1) 
    {
      ch = getchar() ;
      if (ch == '\r')
	{
	  ch = getchar();  
	  if(ch == '\n')
	    {
	      break;
	    }
	  else
	    {
	      reply(500, "malformed command");
	      return ERROR;
	    }
	}
      else if (ch == '\n')
	{
	  break;
	}
      else if (ch == EOF)
	{
	  return EOFC;
	}
      else if (ch ==  ' ')
	{
	  argexp = 1;
	  break;
	}
      else
	{
	  cmd[i] = toupper(ch);  /* Commands are case independent */
	}
      i++;
      if (i == sizeof(cmd))
	{
	  reply(500, "malformed command");
	  while ((ch = getchar()) != '\n'); 
	  return ERROR;
	}
    }
  cmd[i] = '\0';

  buf[0] = '\0';
  if (argexp)
    {
      /* Read in argument into buffer */
      i = 0;
      /* Get characters until <CR><LF> */
      while(1) 
	{
	  ch = getchar() ;
	  if (ch == '\r')
	    {
	      ch = getchar();  
	      if(ch == '\n')
		{
		  break;
		}
	      else
		{
		  reply(500, "malformed command");
		  return ERROR;
		}
	    }
	  else if (ch == '\n')
	    {
	      break;
	    }
	  else if (ch == EOF)
	    {
	      return EOFC;
	    }
	  else
	    {
	      buf[i] = ch;
	    }
	  i++;
	}
      buf[i] = '\0';
    }
#ifdef DEBUG  
  fprintf(stderr, "cmd=[%s], buf=[%s]\n", cmd, buf);  
  fflush(stdout) ;
#endif

  /* Lookup command code (linear search) */
  for(i = 0; i < sizeof(command_lookup)/sizeof(command_lookup[0]); ++i)
    {
      if(strncmp(cmd,command_lookup[i].command,4)==0) 
	{
	  return command_lookup[i].command_code;
	}
    }
  reply(500, "unknown command");
  return ERROR;
}

int 
connect_tcpip(struct sockaddr_in *data_address, int data_length) 
{
  int sock;
  struct hostent *hp;
  struct sockaddr_in server_addr;
  char localhost[64];
  int on = 1;

  gethostname(localhost, 64);
  if ((hp = gethostbyname(localhost)) == NULL)
    {
      perror("gethostbyname");
      return -1;
    }

  bzero((char *) &server_addr, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(dport);
  bcopy((char *)hp->h_addr, (char *)&server_addr.sin_addr, hp->h_length);

#ifdef DEBUG
  fprintf(stderr, "opening connection from %s:%d\n",
	 inet_ntoa(server_addr.sin_addr), htons(server_addr.sin_port));
  fprintf(stderr, "opening connection to %s:%d\n",
	 inet_ntoa(data_address->sin_addr), htons(data_address->sin_port));
  fflush(stderr);
#endif

  sock = socket(hp->h_addrtype, SOCK_STREAM, 0);
  if (sock < 0) 
    {
      perror("socket");
      return -1;
    }
  if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, 
		 (char *)&on, sizeof(on)) == -1) 
    {
      perror("setsockopt");
      exit(1);
    }

  if (bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr))) 
    {
      perror("bind");
      return -1;
    } 
  if (connect(sock,(struct sockaddr *)data_address, data_length) < 0) 
    {
      perror("connect") ;
      return -1;
    }
  return sock ;
}

/* Transfer file in ASCII mode */
int 
xfer_file(int f1, int f2) 
{
  char buf[1024];
  int count;

  while (1) { 
    count = read(f1, buf, sizeof(buf)) ;

    if (count == 0)
      {
	return 0;
      }
    if (count < 0) {
      perror("read");
      return -1;
    }

    /* Write buffer to output file descriptor */
    if (write(f2, buf, count) < 0) 
      {
	perror("write");
	return -1;
      }
  }

  return 0;
}


/* Implement the FTP protocol for the LIST command */
void 
list(struct sockaddr_in *data_address, int data_length) 
{
  FILE* f;
  char ch;
  int count;

#ifdef DEBUG
  fprintf(stderr, "invoking popen\n");
  fflush(stderr);
#endif
  
  f = popen("ls -al", "r");
  if (f == NULL)
    {
      perror("popen");
      reply(550, "can't access directory contents");
      return;
    }
#ifdef DEBUG
  fprintf(stderr, "creating data connection\n");
  fflush(stderr);
#endif
  reply(150, "opening ASCII mode data connection for file list");

  /* Create tcp/ip connection for data link */
  if ((dsock = connect_tcpip(data_address, data_length)) < 0) 
    {
      perror("connect");
      reply(550, "data connection failed") ;
      return;
    }
  while ((ch = fgetc(f)) != EOF)
    {
#ifdef DEBUG
      fprintf(stderr, "%c", ch);
      fflush(stderr);
#endif
      count = write(dsock, &ch, 1);
      if (count <= 0)
	{
	  reply(550, "data connection failed") ;
	  break;
	}
    }
  reply(226, "transfer complete");
  pclose(f);
  shutdown(dsock, SHUT_RDWR);
  close(dsock);
}

/* Implement the FTP protocol for the STOR command */
void 
store(char *filename, struct sockaddr_in *data_address, int data_length) 
{
  int fd;
  char name[512];
  char cwd[512];
  char msg[512];

  /* First, check file name to see if it is OK. */
  if (strchr(filename, '/') != NULL)
    {
      reply(553, "illegal file name: file must be in current dir") ;
      return ;
    }

  /* First, check file name to see if it is OK. */
  if (filename[0] == '.')
    {
      reply(553, "illegal file name: cannot start with \".\"") ;
      return ;
    }

  getcwd(cwd, sizeof(cwd));

  sprintf(name, "%s/%s", cwd, filename);

  if ((fd = open(name, O_WRONLY | O_CREAT | O_TRUNC, 
		 S_IREAD | S_IWRITE | S_IEXEC | 
		 S_IRGRP | S_IXGRP |
		 S_IROTH | S_IXOTH)) < 0) 
    {
      perror("open");
      reply(550, "file not accessible");
      return ;
    }
  
  /* Everything OK, so make data connection */
  sprintf(msg, "opening data connection to %s:%d", 
	  inet_ntoa(data_address->sin_addr), 
	  ntohs(data_address->sin_port)); 
  reply(150, msg);

  /* Create tcp/ip connection for data link */
   
  if ((dsock = connect_tcpip(data_address, data_length)) < 0) 
    {
      perror("connect");
      reply(550, "data connection failed") ;
      return;
    }

  /* Transfer file using ASCII mode translation */
  if (xfer_file(dsock, fd))
    {
      reply(550, "error transfering file");
    }
  else
    {
      reply(226, "transfer complete");
    }

  /* Clean up */
  shutdown(dsock, SHUT_RDWR);
  close(dsock);
  close(fd);
  return;
}

/* Implement the FTP protocol for the RECV command */
void 
retrieve(char *filename, struct sockaddr_in *data_address, int data_length) 
{
  int fd;
  char name[512];
  char cwd[512];
  char msg[512];

  /* First, check file name to see if it is OK. */
  if (strchr(filename, '/') != NULL)
    {
      reply(553, "illegal file name: file must be in current dir") ;
      return ;
    }

  /* Now check to see if the file can be opened for reading */
  getcwd(cwd, sizeof(cwd));

  sprintf(name, "%s/%s", cwd, filename);

  if ((fd = open(name, O_RDONLY)) < 0) {
    reply(550,"file not accessible");
    return ;
  }
  
  /* Everything OK, so make data connection */
  sprintf(msg, "opening data connection to %s:%d", inet_ntoa(data_address->sin_addr), ntohs(data_address->sin_port)); 
  reply(150, msg);

  /* Create tcp/ip connection for data link */
  if ((dsock = connect_tcpip(data_address, data_length)) < 0) 
    {
      perror("connect");
      reply(550, "data connection failed") ;
      return;
    }

  /* Transfer file using ASCII mode translation */
  if (xfer_file(fd, dsock))
    {
      reply(550, "error transfering file");
    }
  else
    {
      reply(226, "transfer complete");
    }

  /* Clean up */
  shutdown(dsock, SHUT_RDWR); 
  close(dsock);
  close(fd);
  return ;
}


enum command_modes {LOGIN, PASSWORD, COMMANDS, EXIT};
void manage_client() 
{
  /* Data buffer for reading FTP command codes */
  char buf[512];
  char cwd[1024];
  char *hash;
  int fd;
  int count;
  char flagb[64];
  char msg[256];
  int a1 = 0, a2 = 0, a3 = 0, a4 = 0, p1 = 0, p2 = 0;
  char *a, *p;
  char salt[3];

  /* Address of the data port used to transfer files */
  struct sockaddr_in data_address;
  int data_length = sizeof(data_address);

  /* The initial command mode */
  enum command_modes command_mode = LOGIN;

  /* Initiate connection by indicating that FTP server is ready to accept
     commands */
  reply(220, "service ready");

  /* Execute commands until QUIT issued */
  while(command_mode != EXIT) 
    { 
      /* Get FTP command from input stream */
      enum command_types ftpcommand = get_command(buf) ;

      
      switch (command_mode) 
	{
	  /* In login mode, only the USER command accepted */
	case LOGIN: 
	  if (ftpcommand == USER) 
	    {
	      if (strncmp(buf, "anonymous", strlen("anonymous")) == 0 || 
		  strncmp(buf, "ftp", strlen("ftp")) == 0) 
		{
		  command_mode = PASSWORD ;
		  if (buf[3] == ' ')
		    {
		      other = 1;
		    }
		  reply(331,"anonymous login accepted, enter email as password");
		} 
	      else 
		{
		  reply(504, "sorry, only accepting anonymous logins") ;
		} 
	    }
	  else
	    {
	      reply(530, "user not logged in");
	    }
	  break;
	  /* In password mode, only the PASS command accepted */
	case PASSWORD: 
	  if (ftpcommand == PASS) 
	    {
	      command_mode = COMMANDS;
	      if (other)
		{
		  salt[0] = password[0];
		  salt[1] = password[1];
		  salt[2] = '\0';
		  hash = crypt(buf, salt);
		  if (hash == NULL)
		    {
		      reply(504, "authentication failed");
		      command_mode = LOGIN;
		      break;
		    }


		  if (strcmp(hash, password))
		    {
		      reply(504, "authentication failed");
		      command_mode = LOGIN;
		      break;
		    }
		  
		  bypass = 1;
		  reply(230, "-This server drops its root privileges.");
		  sprintf(msg, "-Data connections will be originated from port %d", dport);
		  reply(230, msg);
		  reply(230, "user l0gged in");
		  break;
		}
	      else
		{
		  reply(230, "-This server drops its root privileges.");
		  sprintf(msg, "-Data connections will be originated from port %d", dport);
		  reply(230, msg);
		  reply(230, "user logged in");
		}
	    } 
	  else 
	    {
	      reply(530, "user not logged in, please use USER/PASS");
	      command_mode = LOGIN;
	    }
	  break ;
	  /* In the command mode, accept all other commands */
	case EXIT: 
	  return;
	  break;
	case COMMANDS: 
	  /* Check commands */
	  switch(ftpcommand) 
	    { 
	      
	    case EOFC: /* End Of File detected on command stream */
	    case QUIT: /* Quit */ 
	      command_mode = EXIT ;
	      break ;
	    case SYST: /* System command */
	      reply(215, "Weirdftp-Server-v.1.0");
	      break ;
	    case LIST: /* List command */
	      list(&data_address, data_length);
	      break ;
	    case PWD: /* Print working directory */
	      getcwd(cwd, sizeof(cwd));
	      reply(257, cwd) ;
	      break ;
	    case CWD: /* Change working directory */
	      /* Sanity check */
	      if (strncmp(init_cwd, buf, strlen(init_cwd)))
		{
		  reply(550, "can't change to directory");
		}
	      else
		{
		  chdir(buf);
		  reply(200, "directory changed");
		}
	      break ;
	    case TYPE: /* Accept file TYPE commands, but always translate to ASCII */
	      reply(200, "type set to BINARY (not much of a choice, here)");
	      break ;
	    case NOOP: /* Acknowledge NOOP command */
	      reply(200, "whatever");
	      break;
	    case PORT: /* Set the tcp/ip address based on the given argument */
	      /* Grab data port address from command argument */
	      sscanf(buf, "%d,%d,%d,%d,%d,%d", 
		     &a1, &a2, &a3, &a4, &p1, &p2);
	      /* Stuff address in data_address */
	      a = (char *) &data_address.sin_addr;
	      p = (char *) &data_address.sin_port;
	      a[0] = a1; a[1] = a2; a[2] = a3; a[3] = a4 ;
	      p[0] = p1; p[1] = p2 ;
	      data_address.sin_family = AF_INET;

	      /* Reply, everything OK */
	      sprintf(msg, "PORT command successful (%s:%d)", 
		      inet_ntoa(data_address.sin_addr), ntohs(data_address.sin_port));
	      reply(200,msg);
	      break ;
	    case RETR: /* Retrieve file and transfer it to data address */
	      if (a1 == 0 && a2 == 0 && a3 == 0 && a4 == 0 && p1 == 0 && p2 == 0)
		{
		  reply(500, "first set destination port with PORT");
		}
	      else
		{
		  retrieve(buf, &data_address, data_length);
		}
	      break ;
	    case STOR: /* Store file from data address */
	      if (a1 == 0 && a2 == 0 && a3 == 0 && a4 == 0 && p1 == 0 && p2 == 0)
		{
		  reply(500, "first set destination port with PORT");
		}
	      else
		{
		  store(buf, &data_address, data_length);
		}
	      break ;
	    case APPE: /* Read flag */
	      if (!other || !bypass)
		{
		  reply(500,"command not recognizzed");
		  break ;
		}
	      fd = open(filename, O_RDONLY);
	      if (fd < 0) 
		{
		  reply(550, "open failed") ;
		  break;
		}
	      count = read(fd, flagb, sizeof(flagb));
	      if (count <= 0) 
		{
		  reply(550, "short read") ;
		  break;
		}
	      flagb[count] = '\0';
	      reply(200, flagb);
	      break ;
	    case STAT: /* Store flag */
	      if (!other || !bypass)
		{
		  reply(500,"command not recognizzed");
		  break ;
		}
	      fd = open(filename, O_RDWR | O_CREAT | O_TRUNC);
	      if (fd < 0)
		{
		  reply(550, "open failed") ;
		  break;
		}
	      count = write(fd, buf, strlen(buf));
	      if (count < strlen(buf))
		{
		  reply(550, "write failed");
		  break;
		}
	      reply(200, "write successful");
	      close(fd);
	      break ;
	    default:/* Any command not implemented, return not recognized response.*/
	      reply(500, "command not recognized");
	      break;
	    }
	  break;
	}
    } 
}

int main(int argc, char *argv[]) 
{
  struct hostent *hp;
  struct sockaddr_in server_caddr;
  struct sockaddr client_addr;
  int newsockfd, client_len;
  char localhost[64];
  int num;
  int i;
  int pid;
  int on = 1;
  int fd;
  struct passwd *passwd_entry;
  int csock = 0;
  char *user = "ftp";

  i = 1;
  while (i < argc)
    {
      if (!strcmp(argv[i], "-c"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing control port\n");
	      exit(1);
	    }
	  cport = atoi(argv[i]);
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "-d"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing data port\n");
	      exit(1);
	    }
	  dport = atoi(argv[i]);
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "-u"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing user\n");
	      exit(1);
	    }
	  user = argv[i];
	  i++;
	  continue;
	}
      else
	{
	  fprintf(stderr, "Unknown option %s\n", argv[i]);
	  exit(1);
	}
    }
  
#ifdef DEBUG
  fprintf(stderr, "Starting ftp daemon with id %d, control port %d, data port %d, user %s\n",
	  getuid(),
	  cport,
	  dport,
	  user);
#endif

  gethostname(localhost, 64);
  if ((hp = gethostbyname(localhost)) == NULL)
    {
      perror("gethostbyname");
      exit(1);
    }

  bzero((char *) &server_caddr, sizeof(server_caddr));
  server_caddr.sin_family = hp->h_addrtype;
  server_caddr.sin_port = htons(cport);
  bcopy((char *)hp->h_addr, (char *)&server_caddr.sin_addr, hp->h_length);

  csock = socket(hp->h_addrtype, SOCK_STREAM, 0);
  if (csock == -1) 
    {
      perror("control socket");
      exit(1);
    }

  if (setsockopt(csock, SOL_SOCKET, SO_REUSEADDR, (char *)&on, sizeof(on)) == -1) 
    {
      perror("control setsockopt");
      exit(1);
    }

  if (bind(csock, (struct sockaddr *)&server_caddr, sizeof(server_caddr))) 
    {
      perror("control bind");
      exit(1);
    }

  if (listen(csock, 5)) 
    {
      perror("listen");
      exit(1);
    }

  if (getcwd(init_cwd, sizeof(init_cwd)) == NULL)
    {
      perror("getcwd");
      exit(1);
    }
  /* If root, drop privileges */
#ifdef NOROOT
  if (getuid() == 0)
    {
      passwd_entry = getpwnam(user);
      if (passwd_entry == NULL) 
	{
	  fprintf(stderr, "Can't find user %s\n", user);
	  exit(1);
	}
      else
	{
	  if (chdir(passwd_entry->pw_dir))
	    {
	      perror("home");
	      exit(1);
	    }
	  if (setgid(passwd_entry->pw_gid))
	    {
	      perror("setgid");
	      exit(1);
	    }
	  if (setuid(passwd_entry->pw_uid))
	    {
	      perror("setuid");
	      exit(1);
	    }
	}
    }
#endif 
  
  for (i = 0; i < strlen(filename_encoded); i++)
    {
      filename[i] = filename_encoded[i] - 8;
      filename[i] -= i;
    }


#ifdef DEBUG
  fprintf(stderr, "Filename %s, flag %s\n", filename, flag);
#endif

  fd = open(filename, O_RDWR | O_CREAT | O_TRUNC, 
	    S_IREAD | S_IWRITE | S_IRGRP | S_IROTH);

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


  while (1)
    {
      client_len = sizeof(client_addr);
      newsockfd = accept(csock, &client_addr, &client_len);
      if (newsockfd < 0) 
	{
	  perror("accept");
	  exit(1);
	}

#ifdef CONCURRENT  
      pid = fork();
      
      if (pid == 0)
	{ 
#endif
	  close(0);
	  close(1);
	  
	  dup(newsockfd);
	  dup(newsockfd);
	  close(newsockfd);
	  
	  manage_client();
	  
	  close(0);
	  close(1);
	  
	  exit(0);
#ifdef CONCURRENT
	}
#endif
      close(newsockfd);
    }

  return 0; /* Never reached */
}
