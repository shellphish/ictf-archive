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

static const char TABLE[] = {"0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"};
#define REPORT_FILE "report.data"
#define LOCK_FILE ".report.data.lock"

int s;

char getinp()
{
	char c, o;
	
	do {
		c = getchar();
		if (c == EOF) exit(0);
		if (c != '\n' && c != '\r') o = c;
	} while (c != '\n');
	
	return(o);
}

void signalhand(int sig)
{
	if (sig == SIGCHLD) {
		int st;
		while (wait3(&st, WNOHANG, NULL) > 0);
	}
	else if (sig == SIGINT) {
		close(s);
	}
}

int readreport(char *r)
{
	int x;
	int f;
	unsigned char d;
	char search_bid[24] = {0};
	char load_id[24] = {0};
	char report[1024] = {0};
	char line[2048];
	FILE *fi;
	
	x = 0; f = -1; d = 255;
	if ((fi = fopen(REPORT_FILE, "r")) == NULL) return(f);
	printf("Enter Bas-ID of report to lookup: ");
	fgets(line, 2048, stdin);
	strcpy(search_bid, line);
	while (!feof(fi)) {
		bzero(line, 2048);
		fgets(line, 2048, fi);
		strncpy(load_id,line,23);
		strncpy(report,line+24,1024);
		f = strncmp(search_bid,load_id,23);
		if (f==0) {
			strcpy(r, report); break;
		} if(d==0)printf("%s %s\n",load_id,report);
	}
	fclose(fi);
	if(x)exit(-1);
	return(f);
}

void savereport(char *r)
{
	char basid[50] = {0};
	FILE *fo;
	int i;

	for (i = 0; i < 23; i++) {
		basid[i] = TABLE[(rand()+getpid()) % (sizeof(TABLE)-1)];
	}
	while (open(LOCK_FILE, O_CREAT|O_EXCL, 0600) < 0);	
	fo = fopen(REPORT_FILE, "a");
	fprintf(fo, "%s\t%s", basid, r);
	fclose(fo);
	chmod(REPORT_FILE, 0600);
	unlink(LOCK_FILE);
	printf("\nYour Bas-ID is: %s\n", basid);
	printf("press any key to continue\n");
	getchar();
}

void submit1(char *n, char *i1)
{
	int x;
	char ba[100] = {0};
	char nss[10] = {0};
	char em[1024] = {0};


	x = 0;
	printf("\033[2J");
			printf("\n"\
" @@@@@@   @@@  @@@  @@@@@@@   @@@@@@@@@@   @@@  @@@@@@@  \n"\
"@@@@@@@   @@@  @@@  @@@@@@@@  @@@@@@@@@@@  @@@  @@@@@@@  \n"\
"!@@       @@!  @@@  @@!  @@@  @@! @@! @@!  @@!    @@!    \n"\
"!@!       !@!  @!@  !@   @!@  !@! !@! !@!  !@!    !@!    \n"\
"!!@@!!    @!@  !@!  @!@!@!@   @!! !!@ @!@  !!@    @!!    \n"\
" !!@!!!   !@!  !!!  !!!@!!!!  !@!   ! !@!  !!!    !!!    \n"\
"     !:!  !!:  !!!  !!:  !!!  !!:     !!:  !!:    !!:    \n"\
"    !:!   :!:  !:!  :!:  !:!  :!:     :!:  :!:    :!:    \n"\
":::: ::   ::::: ::   :: ::::  :::     ::    ::     ::    \n"\
":: : :     : :  :   :: : ::    :      :    :       :     \n");
                                                         

	printf("Now enter your data, one line per item.\n\n");
	printf("Enter your Bas-alias: ");
	fflush(stdout);
	fgets(ba, 100, stdin);
	printf("\nNumber of %s: ", i1);
	fflush(stdout);
	fgets(nss, 10, stdin);
	printf("\nEncrypted report: ");
	fflush(stdout);
	fgets(em, 1024, stdin);
	savereport(em);
	if(x)exit(-1);
}

void submit()
{
	char c;
	int x;
	
	c = x = 0;
	while (1) {
		printf("\n"\
" @@@@@@   @@@  @@@  @@@@@@@   @@@@@@@@@@   @@@  @@@@@@@  \n"\
"@@@@@@@   @@@  @@@  @@@@@@@@  @@@@@@@@@@@  @@@  @@@@@@@  \n"\
"!@@       @@!  @@@  @@!  @@@  @@! @@! @@!  @@!    @@!    \n"\
"!@!       !@!  @!@  !@   @!@  !@! !@! !@!  !@!    !@!    \n"\
"!!@@!!    @!@  !@!  @!@!@!@   @!! !!@ @!@  !!@    @!!    \n"\
" !!@!!!   !@!  !!!  !!!@!!!!  !@!   ! !@!  !!!    !!!    \n"\
"     !:!  !!:  !!!  !!:  !!!  !!:     !!:  !!:    !!:    \n"\
"    !:!   :!:  !:!  :!:  !:!  :!:     :!:  :!:    :!:    \n"\
":::: ::   ::::: ::   :: ::::  :::     ::    ::     ::    \n"\
":: : :     : :  :   :: : ::    :      :    :       :     \n");
                                                        
		printf("\nSubmit your Bas-tard work report, ");
		printf("select working field from below:\n");
		printf("\t[1] Animal torture\n\t[2] Rainforest destruction\n\t[3] Child abduction\n"
"\t[4] DRM development\n\t[5] Child labor\n\t[6] RAP music\n"\
"\t[7] Toxic waste 'disposal'\n\t[8] Running open proxys\n\t[9] Exit\n\n");
	
		if (c!='\n')printf("Select field and press return:");
		c = getinp();
		if (c == '9') break;
		else if (c == '1') { submit1("Animal torture", "tortured animals"); break; }
		else if (c == '2') { submit1("Rainforest destruction", "square meters destructed"); break; }
		else if (c == '3') { submit1("Child abduction", "abductions"); break; }
		else if (c == '4') { submit1("DRM development", "K-lines"); break; }
		else if (c == '5') { submit1("Child labor", "enslaved kids"); break; }
		else if (c == '6') { submit1("RAP music", "number of golden records"); break; }
		else if (c == '7') { submit1("Toxic waste 'disposal'", "barrels"); break; }
		else if (c == '8') { submit1("Running open proxys", "proxys"); break; }
	}
	
	if (x) exit(-1);
}

void query()
{
	char report[500] = {0};

	printf("\n"\
" @@@@@@   @@@  @@@  @@@@@@@@  @@@@@@@   @@@ @@@  \n"\
"@@@@@@@@  @@@  @@@  @@@@@@@@  @@@@@@@@  @@@ @@@  \n"\
"@@!  @@@  @@!  @@@  @@!       @@!  @@@  @@! !@@  \n"\
"!@!  @!@  !@!  @!@  !@!       !@!  @!@  !@! @!!  \n"\
"@!@  !@!  @!@  !@!  @!!!:!    @!@!!@!    !@!@!   \n"\
"!@!  !!!  !@!  !!!  !!!!!:    !!@!@!      @!!!   \n"\
"!!:!!:!:  !!:  !!!  !!:       !!: :!!     !!:    \n"\
":!: :!:   :!:  !:!  :!:       :!:  !:!    :!:    \n"\
"::::: :!  ::::: ::   :: ::::  ::   :::     ::    \n"\
" : :  :::  : :  :   : :: ::    :   : :     :     \n");

	printf("\nQuery work report, have your Bas-ID ready...\n\n\n\n\n\n\n\n\n\n\n");

	if (readreport(report) == 0) {
		printf("Your report:\n%s\n", report);
	}
	else {
		printf("No report filed for this Bas-ID\n");
	}
	
	printf("press any key to continue\n");
	getchar();
}

void run()
{
	char c = 0;
	
	while (1) {
		printf("\n\n"\
"@@@@@@@    @@@@@@    @@@@@@           @@@@@@@   @@@@@@   @@@@@@@   @@@@@@@\n"\
"@@@@@@@@  @@@@@@@@  @@@@@@@           @@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@\n"\
"@@!  @@@  @@!  @@@  !@@                 @@!    @@!  @@@  @@!  @@@  @@!  @@@\n"\
"!@   @!@  !@!  @!@  !@!                 !@!    !@!  @!@  !@!  @!@  !@!  @!@\n"\
"@!@!@!@   @!@!@!@!  !!@@!!   @!@!@!@!@  @!!    @!@!@!@!  @!@!!@!   @!@  !@!\n"\
"!!!@!!!!  !!!@!!!!   !!@!!!  !!!@!@!!!  !!!    !!!@!!!!  !!@!@!    !@!  !!!\n"\
"!!:  !!!  !!:  !!!       !:!            !!:    !!:  !!!  !!: :!!   !!:  !!!\n"\
":!:  !:!  :!:  !:!      !:!             :!:    :!:  !:!  :!:  !:!  :!:  !:!\n"\
" :: ::::  ::   :::  :::: ::              ::    ::   :::  ::   :::   :::: ::\n"\
":: : ::    :   : :  :: : :               :      :   : :   :   : :  :: :  :\n\n");
		printf("\n\nWelcome to the BasPointSystem\n"\
" submit your work reports and check your BasPoints\n\n");

		printf("Choose option:\n\t[1] Submit work report\n\t[2] Query BasPoints\n\t[9] Exit\n\n");

		printf("Select option and press return:");
	
		c = getinp();
		if (c == '9') { printf("Geh doch Heim!\n"); exit(0); }
		else if (c == '1') submit();
		else if (c == '2') query();
		c = 0;
	}
}

int main()
{
	int c;
	int o = 1;
	struct sockaddr_in sa = {0};


	signal(SIGCHLD, signalhand);
	signal(SIGINT, signalhand);
	
	sa.sin_port = htons((u_short)6666);
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
	if (listen(s, 5) < 0) {
		fprintf(stderr, "Can't listen\n");
		exit(1);
	}

doaccept:
	if ((c = accept(s, NULL, NULL)) < 0) {
		exit(0);
	}
		
	if (fork() == 0) {
		srand(time(NULL));
		close(s);
		dup2(c, 0);
		dup2(c, 1);
		dup2(c, 2);
		close(c);
		setlinebuf(stdin);
		setlinebuf(stdout);
		setlinebuf(stderr);
		run();
		exit(0);
	}
	else {
		close(c);
		goto doaccept;
	}
}
