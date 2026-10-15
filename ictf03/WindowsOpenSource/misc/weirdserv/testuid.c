#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <string.h>
#include <stdlib.h>

int setresuid(uid_t ruid, uid_t euid, uid_t suid);
int setresgid(gid_t rgid, gid_t egid, gid_t sgid);

void usage(char *app)
{
  fprintf(stderr, "Usage: %s -u user -c command", app);
}

int main(int argc, char** argv)
{
  struct passwd *passwd_entry = NULL;
  char *user = NULL;
  char *command = NULL;
  int uid;
  int gid;
  int i;
  int new_uid;
  int new_gid;
  int resu;
  int resg;

  i = 1;
  while (i < argc)
    {
      if (!strcmp(argv[i], "-c"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing command\n");
	      usage(argv[0]);
	      exit(1);
	    }
	  command = argv[i];
	  i++;
	  continue;
	}
      else if (!strcmp(argv[i], "-u"))
	{
	  i++;
	  if (argv[i] == NULL)
	    {
	      fprintf(stderr, "Missing user\n");
	      usage(argv[0]);
	      exit(1);
	    }
	  user = argv[i];
	  i++;
	  continue;
	}
      else
	{
	  fprintf(stderr, "Unknown option %s\n", argv[i]);
	  usage(argv[0]);
	  exit(1);
	}
    }
  
  if ((user == NULL) || (command == NULL))
    {
      usage(argv[0]);
      exit(1);
    }
  
  passwd_entry = getpwnam(user);
  if (passwd_entry == NULL) 
    {
      fprintf(stderr, "Can't find user %s\n", user);
      exit(1);
    }

  uid = getuid();
  gid = getgid();
  fprintf(stderr, "Giving up uid %d, gid %d\n", uid, gid);

  if (setresgid(passwd_entry->pw_gid, passwd_entry->pw_gid, gid))
    {
      perror("setresgid");
      exit(1);
    }
  
  if (setresuid(passwd_entry->pw_uid, passwd_entry->pw_uid, uid))
    {
      perror("setresuid");
      exit(1);
    }
  
  system("id");
  fprintf(stderr, "%s\n", command);
  system(command);

  fprintf(stderr, "Getting back uid %d, gid %d using setuid\n", uid, gid);
  resu = setuid(0);
  resg = setgid(0);
  new_uid = getuid();
  new_gid = getgid();

  fprintf(stderr, "Set[u|g]id returned [%d,%d], my id is now [%d,%d]\n", 
	  resu, resg, new_uid, new_gid);
 
  system("id");      
  if (new_uid != 0 || new_gid != 0)
    {  
      fprintf(stderr, "Setuid failed, now trying setresuid\n");
      system("id");
      fprintf(stderr, "Getting back uid %d, gid %d using setresuid\n", uid, gid);
      if (setresuid(uid, uid, uid))
	{
	  perror("setresuid");
	  exit(1);
	}
      
      if (setresgid(gid, gid, gid))
	{
	  perror("setresgid");
	  exit(1);
	}
      
      system("id");
    }
  return 0;
}
