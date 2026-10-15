#include <stdio.h>
#define _XOPEN_SOURCE
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#ifdef LINUX
#include <crypt.h>
#endif

#define DEFAULT_OFFSET 1

int main(int argc, char *argv[]) 
{
  int encode = 0;
  int offset = 0;
  u_char value = '\0';
  u_char *output = NULL;
  int i = 0;
  char *hash;
  char *salt = "XX";

  if ((argv[1] == NULL) || (argv[2] == NULL))
    {
      fprintf(stderr, "%s [-e|-d|-p] string [offset|salt]\n", argv[0]);
      return 1;
    }
  if (!strcmp(argv[1], "-e"))
    {
      encode = 1;
    }
  else if  (!strcmp(argv[1], "-d"))
    {
      encode = 0;
    }
  else if  (!strcmp(argv[1], "-p"))
    {
      if (argv[3] != NULL)
	{
	  salt = argv[3];
	}
      hash = crypt(argv[2], salt);
      printf("%s\n", hash);
      return 0;
    }
  else
    {
      fprintf(stderr, "Unknown option: %s\n", argv[1]);
      return 1;
    }

  if (argv[3] == NULL)
    {
      offset = DEFAULT_OFFSET;
    }
  else
    {
      offset = atoi(argv[3]);
    }

  output = (char *)malloc(strlen(argv[2]) + 1);

  for (i = 0; i < strlen(argv[2]); i++)
    {
      if (encode)
	{
	  value = ((u_char)argv[2][i]) + offset + i;
#ifdef DEBUG
	  fprintf(stderr, "encoding output[%d] with value %c (\\%x) (input[%d] is %c (\\%d))\n",  
		  i, value, value, i, argv[2][i], argv[2][i]);
#endif

	}
      else
	{
	  value = argv[2][i] - offset - i;
#ifdef DEBUG
	  fprintf(stderr, "encoding output[%d] with value %c (\\%x) (input[%d] is %c (\\%x))\n",  
		  i, value, value, i, argv[2][i], argv[2][i]);
#endif
	}

      output[i] = value;
    }
  output[i] = '\0';

  for (i = 0; i < strlen(argv[2]); i++)
    {
      printf("\\x%x", output[i]);
    }
  printf("\n");

  return 0;
}
    
