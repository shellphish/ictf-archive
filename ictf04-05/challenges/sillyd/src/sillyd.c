#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>
#include <sys/wait.h>
#include <sys/resource.h>

#define HELP ""\
"+HELP This is the simple Silly Auth Server\n"\
" supported commands are REG, AUTH, REVOKE, STATUS, PING and QUIT\n"\
" results are prefixed with +/- for success failure\n"\
" command syntax:\n"\
" REG    <secretID>   => +REG <auth token>\n"\
" AUTH   <auth token> => +AUTH <secretID>\n"\
" REVOKE <auth token> => +REVOKE\n"\
" STATUS              => +STATUS\n"\
" PING   <num>        => +PONG\n"\
"\r\n"

int s;
static const char CS[] = {"0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"};

void silly(int c)
{
	char cmdbuf[2342];
	char id[32];
	char cmd[2048];
	char *cmdbufP = cmdbuf;
	int count;
	int i;
	int bp = sizeof(cmdbuf);
	unsigned char p;
	int r;
	struct stat fs;


	while ((r = read(c, cmdbufP, bp)) > 0) {
		bp -= r; cmdbufP += r;
	
		if (strncasecmp(cmdbuf, "HELP", 4) == 0) {
			write(c, HELP, strlen(HELP));
		}
		else if (strncasecmp(cmdbuf, "QUIT", 4) == 0) goto quit;
		else if (strncasecmp(cmdbuf, "BYE", 3) == 0) goto quit;
		else if (strncasecmp(cmdbuf, "CYA", 3) == 0) goto quit;
		else if (strncasecmp(cmdbuf, "CU", 3) == 0) goto quit;
		else if (strncasecmp(cmdbuf, "CIAO", 4) == 0) goto quit;
		else if (strncasecmp(cmdbuf, "TSCHUESS", 8) == 0) goto quit;
		else if (strncasecmp(cmdbuf, "REG", 3) == 0) {
			int fp;
			do {
				i = 0;
				for (i = 0; i < 31; i++) {
					id[i] = CS[rand() % (sizeof(CS)-1)];
				}
				snprintf(cmd, 2028, "data/%s.txt", id);
			} while (stat(cmd, &fs) == 0);
			fp = open(cmd, O_CREAT|O_RDWR, 0600);
			write(fp, cmdbuf+strlen("REG")+1, strlen(cmdbuf)-strlen("REG")-1);
			close(fp);
			write(c, "+REG ", 5);
			write(c, id, strlen(id));
			write(c, "\r\n", 2);
		}
		else if (strncasecmp(cmdbuf, "AUTH", 4) == 0) {
			count = strlen("AUTH") + 1;
			bzero(id, 32);
			for (i = 0; i < 32; i++) {
				if (count > strlen(cmdbuf)) break;
				id[i] = cmdbuf[count++];	
				if (id[i] >= 'a' && id[i] <= 'z') continue;
				else if (id[i] >= 'A' && id[i] <= 'Z') continue;
				else if (id[i] >= '0' && id[i] <= '9') continue;
				else if (id[i] == '\r' || id[i] == '\n' || id[i] == 0) {
					id[i] = 0; break;
				}
				else {
					goto aerr;
				}
			}
			strcpy(cmd, "data/");
			strncat(cmd, id, 31);
			strcat(cmd, ".txt");
			if (stat(cmd, &fs) == 0) {
				if (fork() == 0) {
					write(c, "+AUTH ", 6);
					snprintf(cmd, 2048, "cat data/%s.txt", id);
					close(2);
					dup2(c, 1);
					system(cmd);
					return;
				}
			}
			else {
			aerr:
				write(c, "-AUTH\r\n", 7);
			}
		}
		else if (strncasecmp(cmdbuf, "REVOKE", 6) == 0) {
			count = strlen("REVOKE") + 1;
			bzero(id, 32);
			for (i = 0; i < 32; i++) {
				if (count > strlen(cmdbuf)) break;
				id[i] = cmdbuf[count++];	
				if (id[i] >= 'a' && id[i] <= 'z') continue;
				else if (id[i] >= 'A' && id[i] <= 'Z') continue;
				else if (id[i] >= '0' && id[i] <= '9') continue;
				else if (id[i] == '\r' || id[i] == '\n' || id[i] == 0) {
					id[i] = 0; break;
				}
				else {
					goto rerr;
				}
			}
			snprintf(cmd, 2028, "data/%s.txt", id);
			if (stat(cmd, &fs) == 0) {
				unlink(cmd);
				write(c, "+REVOKE\r\n", 9);
			}
			else {
			rerr:
				write(c, "-REVOKE\r\n", 7);
			}
		}
		else if (strncasecmp(cmdbuf, "STATUS", 6) == 0) {
			write(c, "+STATUS ", 8);
			if (fork() == 0) {
				close(2);
				dup2(c, 1);
				dup2(c, 0);
				system("echo -n \"number of tokens: \" `ls data/*.txt|wc -l`; echo");
				return;
			}
		}
		else if (strncasecmp(cmdbuf, "PING", 4) == 0) {
			sscanf(cmdbuf+strlen("PING"), "%d", &p);
			do { write(c, "+PONG\r\n", 7); } while (p-- > 1);
		}
		
		if (strchr(cmdbuf, '\n') != NULL || strchr(cmdbuf, '\r') != NULL) { bp = sizeof(cmdbuf); cmdbufP = cmdbuf; }
	}
quit:
	write(c, "+QUIT\r\n", 7);
}

void signalhand(int sig)
{
	if (sig == SIGCHLD) {
		int st;
		while (wait3(&st, WNOHANG, NULL) >=0);
	}
	else if (sig == SIGINT) {
		close(s);
	}
}

int main()
{
	int c;
	int o = 1;
	struct sockaddr_in sa = {0};
	
	srand(time(NULL));
		
	signal(SIGCHLD, signalhand);
	signal(SIGINT, signalhand);
	
	sa.sin_port = htons((u_short)12345);
	sa.sin_family = AF_INET;
	
	if ((s = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		fprintf(stderr, "Can't create socket\n");
		exit(1);
	}
	if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, (char *)&o, sizeof(o)) < 0) {
		fprintf(stderr, "Can't set socket options\n");
		exit(1);
	}
	if (bind(s, (struct sockaddr*) &sa, sizeof(struct sockaddr_in)) < 0) {
		fprintf(stderr, "Can't bind port\n");
		exit(1);
	}
	if (listen(s, 1) < 0) {
		fprintf(stderr, "Can't listen\n");
		exit(1);
	}

	for (;;) {
		if ((c = accept(s, NULL, NULL)) < 0) exit(0);
		if (fork() == 0) {
			close(s);
			write(c, "+READY (SILLY AUTH v42.23)\r\n", 28);
			silly(c);
			close(c);
			exit(0);
		}
		else {
			close(c);
		}
	}
}
