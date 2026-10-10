#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define FILEQUERY_PAGE "\
      <form action=\"/query\" method=\"get\">\n\
      <p>Filename: <input type=\"text\" name=\"filename\"></p>\n\
      <input type=\"hidden\" name=\"user\" value=\"%s\"></p>\n\
      <input type=\"submit\" value=\"Query\"></p>\n\
      </form>\n"

#define FILESTORE_PAGE "\
      <form action=\"/store\" method=\"get\">\n\
      <p>Filename: <input type=\"text\" name=\"filename\"></p>\n\
      <p>Content: <input type=\"textarea\" name=\"content\"></p>\n\
      <input type=\"hidden\" name=\"user\" value=\"%s\"></p>\n\
      <input type=\"submit\" value=\"Store\"></p>\n\
      </form>\n"

#define CORPORATE_PASSWORD "miconsenta"

int main(int argc, char *argv[])
{
  char operation[256];

  if (argc != 4) {
    printf("<p>Biometric authentication failed.</p>\n");
    printf("<p>Cannot access the reader information.</p>\n");
    return 1;
  }
  sscanf(argv[3], "OP-%s", operation);
  if (!strcmp(argv[2], CORPORATE_PASSWORD))
    {
      if (!strcmp(operation, "query"))
	{
	  printf(FILEQUERY_PAGE, argv[1]);
	  fflush(stdout);
	  execlp("touch", "touch", argv[1], 0);
	}
      else if (!strcmp(operation, "store"))
	{
	  printf(FILESTORE_PAGE, argv[1]);
      	  fflush(stdout);
	  execlp("touch", "touch", argv[1], 0);
	}
      else
	{
	  printf("<p>Biometric authentication successful.</p>\n");
	  printf("<p>Unknown operation: <tt>");
	  printf(operation);
	  printf("</tt></p>\n");
	  fflush(stdout);
	}
    }
  else
    {
      printf("<p>Biometric authentication failed.</p>\n");
      printf("<p>Wrong password: <tt>");
      printf(argv[2]);
      printf("</tt></p>\n");
      printf("<p>Put your face closer to the screen and press your finger firmly against the reader.</p>\n");
      printf("<p><a href=\"index.html\">Try again</a>.</p>\n");
      fflush(stdout);
      return 1;
    }
  return 0;
}
