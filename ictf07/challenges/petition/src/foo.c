#include <stdio.h>
#include <string.h>


int main(int argc, char* argv[])
{
  char buf[1024];
  char *ptr = NULL;
  char cmd[1024];
  char res[1024];
  int i = 0;
  int j = 0;
  FILE *f = NULL;

  if (argv[1] == NULL) {
    fprintf(stderr, "MAFIA sanitization tool v. 7.3\n");
    return -1;
  }

  for (i = 0; i < strlen(argv[1]); i++) {
    buf[i] = argv[1][i];
    if (buf[i] == '\r' || buf[i] == '\n') {
      buf[i] = ' ';
    }
  }

  ptr = buf;
  while ((ptr = strpbrk(ptr, "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")) != NULL) {
    for (j = 0; j < strlen(ptr); j++) {
      ptr[j] = ptr[j+1]; 
    }
    ptr[j] = '\0';
    ptr++;
  }

  if ((ptr = strstr(buf, "debug:")) != NULL) {
    ptr = ptr + strlen("debug:");
    sprintf(cmd, "echo %s | sed s/[]\\!\\\"#$%\\&\\'\\(\\)\\*+,\\-\\.\\/:\\;\\<=\\>?@[\\\\\\^_\\`{\\|}~]/\\ /g", ptr); 
    f = popen(cmd, "r");
    ptr = res;
    if (f != NULL) {
      while (fread(ptr, 1, 1, f))
	ptr++;
      *ptr = '\0';
      fclose(f);
    }
    printf(res);
    return 1;
  }

  printf(buf);
  printf("\n");
  return 0;
}
	  
	     
		   
