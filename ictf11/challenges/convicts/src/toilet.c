// CTF11TAG: SERVICE:A AUTODEPLOY USER:PRISON TYPE:CCODE COMPILETO:./bin/toilet COMPILEFLAGS:-lssl
// TODOS: NONE
// STATUS: DONE
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <openssl/md5.h>
#include <openssl/evp.h>
#include <libgen.h>
#include <unistd.h>

char *basename(char *arg)
{
	if (strlen(arg) == 0)
	{
		arg[0] = '.';
		arg[1] = '\0';
		return arg;
	}

	char *dfile = strrchr(arg, '/');
	if (dfile)
	{
		*dfile = '\0';
		strncpy(arg, dfile+1, strlen(dfile+1));
		dfile = arg;

		return dfile;
	}
	else
	{
		return arg;
	}
}

// let's hope there's not an unintended vuln somewhere here :-)
int main(int argc, char **argv)
{
	char result[MD5_DIGEST_LENGTH];
	char resulthex[1024];
	char cafe_cmd[1024] = {0};
	char *cafe_food;
	char *cafe_action;
	char msg[1024] = {0};
	int i;
	FILE *src;
	FILE *dst;
	int ssize;
	int dsize;
	char dirt[2048];
	char dt[] = "./jailcell/toilet/tunnel/crap_XXXXXX";
	char ds[] = "./excercize_yard/sand/message_XXXXXX";
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
			printf("Can't check now, the guards are watching!!! Go chill out in your cell!\n");
			exit(1);
		}

		system("/bin/ls -1 ./jailcell/toilet/tunnel/ | /usr/bin/xargs -I {} /usr/bin/touch ./excercize_yard/sand/{}");
		printf("Ok, dude. You keep a lookout, I'll check out what's down there. I'm gonna write the results in the sand in the excercise yard!\n");
	}
	else if (strcmp(argv[1], "sweep") == 0)
	{
		printf("You read the list? I'll sweep it up!\n");
		system("/bin/rm ./excercize_yard/sand/*");
	}
	else if (strcmp(argv[1], "retrieve") == 0)
	{
		if (argc < 3)
		{
			printf("What're you retrieving?\n");
			exit(1);
		}

		if (argc < 4)
		{
			printf("What's the secret?\n");
			exit(1);
		}

		src = fopen(argv[2], "rb");
		if (!src)
		{
			printf("Can't find your item!!\n");
			exit(1);
		}

		fread(msg, 1, 1023, src);

		MD5(msg, strlen(msg), result);
		for(i=0; i < MD5_DIGEST_LENGTH; i++) sprintf(resulthex + 2*i, "%02x", (unsigned char) result[i]);

		if (strcmp(resulthex, argv[3]) == 0)
		{
			printf("Ok, here you go: %s\n", msg);
		}
		else
		{
			printf("Wrong secret, go away!\n");
		}
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
		printf("Writing message %s on the sand!!!\n", dfile);
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
		printf("Flushing the evidence to %s!!!\n", dfile);
		fwrite(argv[2], strlen(argv[2]), 1, dst);
	}
	else if (strcmp(argv[1], "cafeteria") == 0)
	{
		if (argc < 3)
		{
			printf("Which meal?\n");
			exit(1);
		}

		if (argc < 4)
		{
			printf("What action?");
			exit(1);
		}

		cafe_food = basename(argv[3]);
		cafe_action = basename(argv[2]);

		for (i = 0; i < strlen(cafe_action); i++)
		{
			if ((cafe_action[i] >= 'A' && cafe_action[i] <= 'Z') || (cafe_action[i] >= 'a' && cafe_action[i] <= 'z') || (cafe_action[i] >= '0' && cafe_action[i] <= '9') || cafe_action[i] == '_')
			{
				// good
			}
			else
			{
				cafe_action[i] = '.';
			}
		}
		for (i = 0; i < strlen(cafe_food); i++)
		{
			if ((cafe_food[i] >= 'A' && cafe_food[i] <= 'Z') || (cafe_food[i] >= 'a' && cafe_food[i] <= 'z') || (cafe_food[i] >= '0' && cafe_food[i] <= '9') || cafe_food[i] == '_')
			{
				// good
			}
			else
			{
				cafe_food[i] = '.';
			}
		}

		strncat(cafe_cmd, cafe_action, 255);
		strcat(cafe_cmd, " ./cafeteria/cupboard/");
		strncat(cafe_cmd, cafe_food, 255);

		puts(cafe_cmd);
		system(cafe_cmd);
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

		chdir("./jailcell/toilet/tunnel/");
		sprintf(dirt, "/bin/cp %s ../../../cafeteria/cupboard/$(/usr/bin/md5sum %s | /usr/bin/cut -f1 -d' ' | /usr/bin/md5sum | /usr/bin/cut -f1 -d' ')", dfile, dfile);
		system(dirt);
	}

	exit(0);
}
