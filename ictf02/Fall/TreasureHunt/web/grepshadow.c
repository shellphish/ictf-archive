#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <pwd.h>
#include <string.h>

int main(int argc, char** argv)
{
  char *cmd;
  uid_t uid;
  struct passwd *passwd_entry;

  if ((argv[1] == NULL) || (argv[2] == NULL)) {
    fprintf(stderr, "missing arg\n"); 
    exit(1);
  }
  passwd_entry = getpwuid(atoi(argv[1]));
  if (passwd_entry == NULL) {
    fprintf(stderr, "missing entry\n"); 
    exit(1);
  }

  uid = getuid();
  if (uid != passwd_entry->pw_uid) {
    fprintf(stderr, "wrong user\n"); 
    exit(1);
  }

  cmd = (char *)malloc(strlen(argv[2]) + 
		       strlen("/bin/grep ") +
		       strlen(" /etc/shadow") + 1);
  sprintf(cmd, "/bin/grep %s /etc/shadow", argv[2]);
  setuid(0);
  system(cmd);
  exit(0);
}



