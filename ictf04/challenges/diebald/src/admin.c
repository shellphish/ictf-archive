#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <string.h>


#define STD_HEADER "\
Content-Type: text/html\r\n\
\r\n\
<html>\n\
  <head>\n\
    <title>Administration Page</title>\n\
    <link href=\"/diebald/diebald.css\" rel=\"stylesheet\" type=\"text/css\" />\n\
  </head>\n\
  <body>\n\
    <div id=\"container\">\n\
      <div id=\"intro\">\n\
        <h1><span>Admininistration Page</span></h1>\n"

#define STD_TAIL "\
      </div>\n\
    </div>\n\
  </body>\n\
</html>\n"

#define LOGIN_FORM "\
    <h2><span>Create a new Die-Bald Administrator</span></h2>\n\
    <form action=\"/cgi-bin/admin\" method=\"get\">\n\
      <p><label for=\"username\">Username:</label>\n\
	<input type=\"text\" name=\"username\" id=\"username\" /></p>\n\
      <p><label for=\"password\">Password: </label>\n\
	<input type=\"password\" name=\"password\" id=\"password\" /></p>\n\
	<input type=\"hidden\" name=\"op\" value=\"create\" /></p>\n\
      <p><input type=\"submit\" value=\"Create login\" /></p>\n\
    </form>\n\
    <h2><span>Assign a task to a Die-Bald Administrator</span></h2>\n\
    <form action=\"/cgi-bin/admin\" method=\"get\">\n\
      <p><label for=\"username\">Username:</label>\n\
	<input type=\"text\" name=\"username\" id=\"username\" /></p>\n\
      <p><label for=\"password\">Password: </label>\n\
	<input type=\"password\" name=\"password\" id=\"password\" /></p>\n\
      <p><label for=\"task\">Task: </label>\n\
	<input type=\"text\" name=\"task\" id=\"password\" /></p>\n\
	<input type=\"hidden\" name=\"op\" value=\"addtask\" /></p>\n\
      <p><input type=\"submit\" value=\"Add Task\" /></p>\n\
    </form>\n\
    <h2><span>Review the tasks of a Die-Bald Administrator</span></h2>\n\
    <form action=\"/cgi-bin/admin\" method=\"get\">\n\
      <p><label for=\"username\">Username:</label>\n\
	<input type=\"text\" name=\"username\" id=\"username\" /></p>\n\
      <p><label for=\"password\">Password: </label>\n\
	<input type=\"password\" name=\"password\" id=\"password\" /></p>\n\
	<input type=\"hidden\" name=\"op\" value=\"gettask\" /></p>\n\
      <p><input type=\"submit\" value=\"Review Tasks\" /></p>\n\
    </form>\n"

#define TASKFILE "tasks.txt"

int debug = 0;

void manage_request()
{
  int i = 0;
  char taskfile[256];
  char buf[256];
  char *op = NULL;
  char *username = NULL;
  char *password = NULL;
  char *task = NULL;
  char *field = NULL;
  char *newfield = NULL;
  char *end = NULL;
  char *value = NULL;
  FILE *f = NULL;
  char storedpwd[64];
  char taskline[64];
  int pwdl;

  strcpy(taskfile, TASKFILE);
  strcpy(buf, getenv("QUERY_STRING"));

  if (strlen(buf) == 0)
    {
      printf(LOGIN_FORM);
      goto end;
    }
  if (debug)
    {
      printf("<p>Parsing <tt>%s</tt></p>\n", buf);
    }

  field = buf;
  while (1)
    {
      end = strchr(field, '&');
      if (end != NULL)
	{
	  newfield = end + 1;
	  *end = '\0';
	}
      if ((value = strstr(field, "op=")) != NULL)
	{
	  op = field + strlen("op=");
	}
      else if ((value = strstr(field, "username=")) != NULL)
	{
	  username = field + strlen("username=");
	}
      else if ((value = strstr(field, "password=")) != NULL)
	{
	  password = field + strlen("password=");
	}
      else if ((value = strstr(field, "task=")) != NULL)
	{
	  task = field + strlen("task=");
	}
      else
	{
	  printf("<p>Unknown field %s.</p>\n", field);
	  goto end;
	}
      if (end == NULL) break;
      field = newfield;
    }
  
  if (debug)
    {
      printf("<p>Parsed op=%s, username=%s, password=%s, task=%s</tt></p>\n", 
	     op, username, password, task);
    }
  fflush(stdout);
  if (op == NULL)
    {
      printf("<p>Missing required operation field.</p>\n");
      goto end;
    }
  if ((username == NULL) || (password == NULL))
    {
      printf("<p>Missing required username and password.</p>\n");
      goto end;
    }

  if (!strcmp(op, "create"))
    {
      f = fopen(username, "w+");
      if (f == NULL)
	{
	  printf("<p>Cannot create account.</p>\n");
	  goto end;
	}
	  
      fprintf(f, "%s", password);
      fclose(f);
      printf("<p>Account successfully created.</p>\n");
      printf("<p>Return to the <a href=\"/cgi-bin/admin\">main page</a>.</p>\n");
      
    }
  else if (!strcmp(op, "addtask")) 
    {
      if (task == NULL)
	{
	  printf("<p>Missing required task.</p>\n");
	  goto end;
	}
      f = fopen(username, "r");
      if (f == NULL)
	{
	  printf("<p>Non-existent user.</p>\n");
	  goto end;
	}
      fgets(storedpwd, 64, f);
      pwdl = strlen(storedpwd);
      if (storedpwd[pwdl - 1] == '\n')
	{
	  storedpwd[pwdl - 1] = '\0';
	}
      fclose(f);
      if (debug)
	{
	  printf("<p>Comparing stored <tt>[%s]</tt> with provided <tt>[%s]</tt>\n", storedpwd, password);
	}
      if (strcmp(storedpwd, password))
	{
	  printf("<p>Wrong password.</p>\n");
	  goto end;
	}
      f = fopen(taskfile, "a");
      if (f == NULL)
	{
	  printf("<p>Can't open task file.</p>\n");
	  goto end;
	}
      fprintf(f, "%s:%s\n", username, task);
      fclose(f);
      printf("<p>The task \" \%s\" was assigned to user \"%s\".</p>\n", task, username);
    }
  else if (!strcmp(op, "gettask")) 
    {
      f = fopen(username, "r");
      if (f == NULL)
	{
	  printf("<p>Non-existent user.</p>\n");
	  goto end;
	}
      fgets(storedpwd, 64, f);
      pwdl = strlen(storedpwd);
      if (storedpwd[pwdl - 1] == '\n')
	{
	  storedpwd[pwdl - 1] = '\0';
	}
      fclose(f);
      if (strcmp(storedpwd, password))
	{
	  printf("<p>Wrong password.</p>\n");
	  goto end;
	}
      f = fopen(taskfile, "r");
      if (f == NULL)
	{
	  printf("<p>Can't open task file.</p>\n");
	  goto end;
	}
      printf("<p>Task to be done by %s:</p>\n<pre>\n", username);
      while (fgets(taskline, 256, f))
	{
	  if (!isalnum(taskline[0])) continue;
	  end = strchr(taskline, ':');
	  if (end == NULL)
	    {
	      printf("<p>Malformed task file.</p>\n");
	      goto end;
	    }
	  *end = '\0';
	  end++;
	  if (!strcmp(taskline, username))
	    {
	      printf(end);
	    }
	}
      printf("</pre>\n");
      fclose(f);
    }
  else
    {
      printf("<p>Unknown operation: %s.</p>\n", op);
      goto end;
    }
 end:
  if (i != 0)
    {
      printf("<p>Somebody tried a buffer overflow. The Die-Bald anti-overflow system caught the attempt\n</p>");
      fflush(stdout);
      exit(1);
    }
  return;
    }

int main(int argc, char *argv[])
{
  printf(STD_HEADER);

  manage_request();

  printf(STD_TAIL);
  return 0;
  
}
