// CTF11TAG: SERVICE:A AUTODEPLOY USER:PRISON TYPE:CCODE COMPILETO:/home/convicts/bin/toilet COMPILEFLAGS:-lssl
// TODOS: NONE
// STATUS: DONE
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <openssl/md5.h>
#include <openssl/evp.h>
#include <libgen.h>

// let's hope there's not an unintended vuln somewhere here :-)
int main(int argc, char **argv)
{
	char result[MD5_DIGEST_LENGTH];
	char resulthex[1024];
	int i;
	FILE *src;
	FILE *dst;
	int ssize;
	int dsize;
	char dirt[2048];
	char dt[] = "/home/convicts/jailcell/toilet/tunnel/crap_XXXXXX";
	char ds[] = "/home/convicts/excercize_yard/sand/message_XXXXXX";
	char *dfile;

	if (argc < 2)
	{
		printf("Do what??\n");
		exit(1);
	}

	// there are several modes to this. Fred, when you're writing the score script, you
	// really only need to use "flush"
	if (strcmp(argv[1], "look") == 0)
	{
		// make sure the message exists
		if (argc < 3)
		{
			printf("What's the message from the lookouts?? We can't mess with the toilet unless it's safe!\n");
			exit(1);
		}

		MD5(argv[2], strlen(argv[2]), result);
		for(i=0; i < MD5_DIGEST_LENGTH; i++) sprintf(resulthex + 2*i, "%02x", (unsigned char) result[i]);

		// this looks random, but it's the MD5 of 'OKTODIGNOW!', no newline
		// note, we should NOT use this in the clear when checking the script
		if (strcmp(resulthex, "319f1c21d4d43543c1c7d0ac18a56f27") != 0)
		{
			printf("Can't check now, the guards are watching!!! Go chill out in your cell.ictf2011.info!\n");
			exit(1);
		}

		system("/bin/ls -1 /home/convicts/jailcell/toilet/tunnel/ | /usr/bin/xargs -I {} /usr/bin/touch /home/convicts/excercize_yard/sand/{}");
		printf("Ok, dude. You keep a lookout, I'll check out what's down there. I'm gonna write the results in the sand in the excercise yard!\n");
	}
	else if (strcmp(argv[1], "sweep") == 0)
	{
		printf("You read the list? I'll sweep it up!\n");
		system("/bin/rm /home/convicts/excercize_yard/sand/*");
	}
	else if (strcmp(argv[1], "draw") == 0)
	{
		if (argc < 3)
		{
			printf("The guards are getting suspicious that we're spending so much time at the excercize yard! We gotta pretend to draw something in the sand. What should we draw??\n");
			exit(1);
		}

		dfile = mktemp(ds);
		dst = fopen(dfile, "wb");
		if (dst == NULL)
		{
			perror("WTF!!! The sand's erroring out");
			exit(1);
		}
		printf("Writing message %s on the sand!!!\n", basename(dfile));
		fwrite(argv[2], strlen(argv[2]), 1, dst);
	}
	else if (strcmp(argv[1], "flush") == 0)
	{
		if (argc < 3)
		{
			printf("What should I flush, man??\n");
			exit(1);
		}

		dfile = mktemp(dt);
		dst = fopen(dfile, "wb");
		if (dst == NULL)
		{
			perror("WTF!!! The toilet's erroring out");
			exit(1);
		}
		printf("Flushing the evidence to %s!!!\n", basename(dfile));
		fwrite(argv[2], strlen(argv[2]), 1, dst);
	}
	else if (strcmp(argv[1], "fish") == 0)
	{
		if (argc < 3)
		{
			printf("Fish for what??\n");
			exit(1);
		}

		dfile = basename(argv[2]);

		for (i = 0; i < strlen(dfile); i++)
		{
			if ((dfile[i] >= 'A' && dfile[i] <= 'Z') || (dfile[i] >= 'a' && dfile[i] <= 'z') || (dfile[i] >= '0' && dfile[i] <= '9') || dfile[i] == '_' || dfile[i] == '/')
			{
				// good
			}
			else
			{
				dfile[i] = '.';
			}
		}

		chdir("/home/convicts/jailcell/toilet/tunnel/");
		sprintf(dirt, "/bin/cp %s ../../../cafeteria/cupboard/$(/usr/bin/md5sum %s | /usr/bin/cut -f1 -d' ')", dfile, dfile);
		system(dirt);
	}

	exit(0);
}
