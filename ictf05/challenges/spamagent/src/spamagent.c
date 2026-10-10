/* Author: Massimo Zanardi (c) 2003-2005 */

#include <stdio.h> 
#include <string.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <tcl.h>
#include <libxml/parser.h>
#include <libxml/tree.h>

#include <regex.h>
#include <mydiag.h>
#include <zocket.h>

#define AGENTMAXSIZE 8192
#define AGENT_START_TAG "<agent>"
#define AGENT_END_TAG "</agent>"

#define MSG_ERR_READ "Error: Cannot read from server"
#define MSG_ERR_NODATA "Error: Cannot extract agent data from message"
#define MSG_ERR_PARSE "Error: Cannot parse agent data"
#define MSG_REPLY_TCL_OK "%s\n"
#define MSG_REPLY_TCL_ERROR "Tcl Error: %s\n%s\n"

/* #define DEBUG
   #define DEBUG2  */
#define CHUNKSIZE 1024
#define DIRSIZE 1024

struct data_item {
  xmlChar *label;
  xmlChar *value;
  struct data_item *next;
  struct data_item *prev;
};

struct agent_descr {
  xmlChar* username;
  xmlChar* password;
  struct data_item data;
  xmlChar* code;
  xmlChar* results;
};

void
send_reply(char *string)
{
  assert(string);

  fprintf(stdout, 
	  "Content-Length: %d\r\nContent-Type: text/plain\r\n\r\n%s",
	  (int)strlen(string), string);

  fflush(stdout);
  return;
}

int ResultsCommand(ClientData client_data, 
		Tcl_Interp* interp, 
		int argc, char *argv[])
     
{    
  struct agent_descr *agent;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "executing command results");
#endif
  
  /* Reset result data. */
  Tcl_ResetResult(interp);

  /* Check number of arguments. */
  if (argc < 2) 
    {
      Tcl_AppendResult(interp, 
		       "ERROR: results requires a subcommand (get or set)\n",
		       (char*) NULL); 
      
      return TCL_ERROR;
    }

  agent = (struct agent_descr *)client_data;
  assert(agent);

#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "current results are: %s", agent->results);
#endif
  
  if (!strcmp(argv[1], "set"))
    {
      if (argc < 3)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: results set subcommand requires a value\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}
      
      /* Find item */
      if (agent->results)
	{
	  xmlFree(agent->results);
	}
      agent->results = xmlCharStrdup(argv[2]);
      assert(agent->results);

#ifdef DEBUG2
      my_debug(__FILE__, __LINE__, "results set to: %s", agent->results);
#endif

      Tcl_SetResult(interp, (char *)agent->results, TCL_VOLATILE);
    }
  else if (!strcmp(argv[1], "get"))
    {
      if (argc >= 3)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: too many args for results get subcommand\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}

#ifdef DEBUG2
      my_debug(__FILE__, __LINE__, "results returned: %s", agent->results);
#endif

      Tcl_SetResult(interp, (char *)agent->results, TCL_VOLATILE);
    }
  else
    {
      Tcl_AppendResult(interp, 
		       "ERROR: unknown results command ",
		       argv[1],
		       "\n",
		       (char*) NULL); 
      
      return TCL_ERROR;
    }

  return TCL_OK;
}

int DataCommand(ClientData client_data, 
		Tcl_Interp* interp, 
		int argc, char *argv[])
     
{    
  struct agent_descr *agent;
  struct data_item *item;
  int found;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "executing command data");
#endif

  /* Reset result data. */
  Tcl_ResetResult(interp);

  /* Check number of arguments. */
  if (argc < 2) 
    {
      Tcl_AppendResult(interp, 
		       "ERROR: data requires a subcommand (get or set)\n",
		       (char*) NULL); 
      
      return TCL_ERROR;
    }

  agent = (struct agent_descr *)client_data;
  assert(agent);
  
  if (!strcmp(argv[1], "set"))
    {
      if (argc < 4)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: data set subcommand requires a key and a value\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}
      
      /* Find item */
      found = 0;
      for (item = agent->data.next; item != &(agent->data); item = item->next)
	{
	  if (!xmlStrcmp(item->label, (xmlChar *)argv[2]))
	    {
#ifdef DEBUG2
	      my_debug(__FILE__, __LINE__, "modifying item %s with value %s", 
		    (char *)item->label, 
		    (char *)item->value);
#endif

	      xmlFree(item->value);
	      item->value = xmlCharStrdup(argv[3]);
	      assert(item->value);
	      found = 1;
	      break;
	    }	      
	}
      if (!found)
	{
#ifdef DEBUG2
	  my_debug(__FILE__, __LINE__, "creating new item %s with value %s", 
		    argv[2], 
		    argv[3]);
#endif

	  item = (struct data_item *)malloc(sizeof(struct data_item));
	  assert(item);
	  item->label = xmlCharStrdup(argv[2]);
	  assert(item->label);
	  item->value = xmlCharStrdup(argv[3]);
	  assert(item->value);
	  item->next = &(agent->data);
	  item->prev= agent->data.prev; 
	  agent->data.prev = item;
	  item->prev->next = item;
	}
      Tcl_SetResult(interp, (char *)item->value, TCL_VOLATILE);
    }
  else if (!strcmp(argv[1], "get"))
    {
      if (argc < 3)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: data get subcommand requires a key\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}
      
      /* Find item */
      found = 0;
      for (item = agent->data.next; item != &(agent->data); item = item->next)
	{
	  if (!xmlStrcmp(item->label, (xmlChar *)argv[2]))
	    {
#ifdef DEBUG2
	      my_debug(__FILE__, __LINE__, "found item %s with value %s", 
		    (char *)item->label, 
		    (char *)item->value);
#endif

	      Tcl_SetResult(interp, (char *)item->value, TCL_VOLATILE);
	      found = 1;
	      break;
	    }	      
	}
      if (!found)
	{
	  Tcl_SetResult(interp, NULL, 0);
	}
    }
  else
    {
      Tcl_AppendResult(interp, 
		       "ERROR: unknown data command ",
		       argv[1],
		       "\n",
		       (char*) NULL); 
      
      return TCL_ERROR;
    }

  return TCL_OK;
}

int StoreCommand(ClientData client_data, 
		 Tcl_Interp* interp, 
		 int argc, char *argv[])
     
{    
  struct agent_descr *agent;
  int i = 0;
  FILE *f = NULL;
  char contents[2048];
  
#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "executing command store");
#endif

  /* Reset result data. */
  Tcl_ResetResult(interp);

  /* Check number of arguments. */
  if (argc < 2) 
    {
      Tcl_AppendResult(interp, 
		       "ERROR: data requires a subcommand (get or set)\n",
		       (char*) NULL); 
      
      return TCL_ERROR;
    }

  agent = (struct agent_descr *)client_data;
  assert(agent);
  
  if (!strcmp(argv[1], "set"))
    {
      if (argc < 4)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: store set subcommand requires a key and a value\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}

#ifdef DEBUG2
      my_debug(__FILE__, __LINE__, "creating stored item %s with value %s", 
	       argv[2], 
	       argv[3]);
#endif
      
      if ((f = fopen(argv[2], "w+")) == NULL) 
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: cannot open file\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}
      
      if (fwrite(argv[3], 1, strlen(argv[3]), f) <= 0)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: cannot write to file\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}
      fclose(f);

      Tcl_SetResult(interp, (char *)argv[3], TCL_VOLATILE);
    }
  else if (!strcmp(argv[1], "get"))
    {
      if (argc < 3)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: store get subcommand requires a key\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}
      
      if ((f = fopen(argv[2], "r")) == NULL) 
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: cannot open file\n",
			   (char*) NULL); 
	  
	  return TCL_ERROR;
	}

      i = 0;
      while (fread(&(contents[i]), 1, 1, f))
	{
	  i++;
	}
      contents[i] = '\0';

#ifdef DEBUG2
      my_debug(__FILE__, __LINE__, "found stored item %s with value %s", 
	       argv[2], 
	       contents);
#endif

      fclose(f);

      Tcl_SetResult(interp, (char *)contents, TCL_VOLATILE);
    }
  else
    {
      Tcl_AppendResult(interp, 
		       "ERROR: unknown store sub command ",
		       argv[1],
		       "\n",
		       (char*) NULL); 
      
      return TCL_ERROR;
    }
  
  return TCL_OK;
}


#define URL_RFC_REGEX "^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?"
#define URL_ORIG_REGEX "^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?"
#define URL_REGEX "^(([^:/?#]+):)?(//([^/:?#]*)(:([^/]*))*)?([^?#]*)(\\?([^#]*))?(#(.*))?"
#define MAX_MATCH 16
#ifdef COMMENT
typedef struct {
        int re_magic;
        size_t re_nsub;         /* number of parenthesized subexpressions */
        __const char *re_endp;  /* end pointer for REG_PEND */
        struct re_guts *re_g;   /* none of your business :-) */
} regex_t;

typedef struct {
        regoff_t rm_so;         /* start of match */
        regoff_t rm_eo;         /* end of match */
} regmatch_t;
#endif

int GoCommand(ClientData client_data, Tcl_Interp* interp, 
	      int argc, char *argv[])
{    
  int len = 0;
  struct agent_descr *agent = NULL;
  struct data_item *item = NULL;
  char *data = NULL;
  char *items_str = NULL;
  int items_size = 0;
  int items_len = 0;
  int item_len = 0;
  int socket = 0;
  int ret = 0;
  regex_t myregex;
  regmatch_t pmatch[MAX_MATCH];
  char errbuf[CHUNKSIZE];
  int i = 0, j = 0;
  char *url = NULL;
  char *host = NULL;
  char *proto = NULL;
  char *port = NULL;
  char *cgiprog = NULL;
  int tcl_ret = TCL_OK;
  char content_len_str[CHUNKSIZE];
  char *reply = NULL;
  char *reply_body = NULL;
  char *result = NULL;
  int reply_size = 0;
  char c = 0;
  int index = 0;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "executing command go");
#endif
  fflush(stderr);

  /* Reset result data. */
  Tcl_ResetResult(interp);

  /* Check number of arguments. */
  if (argc != 2) 
    {
      Tcl_AppendResult(interp, 
		       "ERROR: go requires an argument\n",
		       (char*) NULL); 
      
      tcl_ret = TCL_ERROR;
      goto end;
    }

  url = strdup(argv[1]);
  assert(url);
  ret = regcomp(&myregex, URL_REGEX, REG_EXTENDED);

  if (ret)
    {

      regerror(ret, &myregex, errbuf, CHUNKSIZE);
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "refcomp failed: %s", errbuf);
#endif

      Tcl_AppendResult(interp, 
		       "ERROR: regular expression compilation failed\n",
		       (char *)NULL);
      
      tcl_ret = TCL_ERROR;
      goto end;
    }

#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "Compiled regex with %u subexpressions\n", 
	   (unsigned int)myregex.re_nsub);
#endif

  ret = regexec(&myregex, url, MAX_MATCH, pmatch, 0);
  
  if (ret)
    {
#ifdef DEBUG
      regerror(ret, &myregex, errbuf, CHUNKSIZE);
      my_debug(__FILE__, __LINE__, "refcomp failed: %s", errbuf);
#endif
      Tcl_AppendResult(interp, "ERROR: regex execution failed\n",
		       (char *)NULL);

      tcl_ret = TCL_ERROR;
      goto end;
    }

#ifdef DEBUG2
  for (i = 0; i < MAX_MATCH; i++)
    {
      fprintf(stderr, "Subexpr %d from %d to %d:\n\t", i, 
	      (int)pmatch[i].rm_so, 
	      (int)pmatch[i].rm_eo);
      for (j = pmatch[i].rm_so; j <  pmatch[i].rm_eo; j++)
	{
	  fputc(argv[1][j], stderr);
	}
      fputc('\n', stderr);
    }
#endif

  len = pmatch[2].rm_eo - pmatch[2].rm_so;
  if (len <= 0)
    {
      Tcl_AppendResult(interp, 
		       "ERROR: missing protocol in go URL\n",
		       (char *)NULL);
      tcl_ret = TCL_ERROR;
      goto end;
    }
  proto = malloc(len + 1); 
  assert(proto);

  i = 0;
  for (j = pmatch[2].rm_so; j <  pmatch[2].rm_eo; j++)
    {
      proto[i] = url[j];
      i++;
    }
  proto[i] = '\0';

  len = pmatch[4].rm_eo - pmatch[4].rm_so;
  if (len <= 0)
    {
      Tcl_AppendResult(interp, 
		       "ERROR: missing hostname in go URL\n",
		       (char *)NULL);
      tcl_ret = TCL_ERROR;
      goto end;
    }
  host = malloc(len + 1); 
  assert(host);

  i = 0;
  for (j = pmatch[4].rm_so; j <  pmatch[4].rm_eo; j++)
    {
      host[i] = url[j];
      i++;
    }
  host[i] = '\0';

  len = pmatch[7].rm_eo - pmatch[7].rm_so;
  if (len <= 0)
    {
      Tcl_AppendResult(interp, 
		       "ERROR: missing CGI program in go URL\n",
		       (char *)NULL);
      tcl_ret = TCL_ERROR;
      goto end;
    }
  cgiprog = malloc(len + 1); 
  assert(cgiprog);

  i = 0;
  for (j = pmatch[7].rm_so; j <  pmatch[7].rm_eo; j++)
    {
      cgiprog[i] = url[j];
      i++;
    }
  cgiprog[i] = '\0';

  len = pmatch[6].rm_eo - pmatch[6].rm_so;
  if (len != 0)
    {
      port = malloc(len + 1); 
      assert(port);

      i = 0;
      for (j = pmatch[6].rm_so; j <  pmatch[6].rm_eo; j++)
	{
	  port[i] = url[j];
	  i++;
	}
      port[i] = '\0';
    }
  else
    {
      port = strdup("80");
      assert(port);
    }

  regfree(&myregex);

#ifdef DEBUG2
  my_debug(__FILE__, __LINE__,
	   "url [%s]\nproto [%s]\nhost [%s]\nCGI prog [%s]\nport [%s]",
	   url, proto, host, cgiprog, port);
#endif

  agent = (struct agent_descr *)client_data;
  assert(agent);
  
  /* Create the body of a mime message */
  len = strlen("------------0xKhTmLbOuNdArY\r\n");
  len += strlen("Content-Disposition: form-data\r\n");
  len += strlen("Content-Type: text/xml\r\n\r\n");
  len += strlen("<agent>\n</agent>\n");
  len += strlen("  <sender>\n  </sender>\n");
  len += xmlStrlen(agent->username);  
  len += strlen("    <user></user>\n");
  len += xmlStrlen(agent->password);  
  len += strlen("    <password></password>\n");
  len += strlen("  <data>\n  </data>\n");
  
  items_str = (char *)malloc(CHUNKSIZE);
  assert(items_str);
  items_size = CHUNKSIZE;
  items_len = 0;
  items_str[0] = '\0';

  for (item = agent->data.next; item != &(agent->data); item = item->next)
    {
      item_len = xmlStrlen(item->label) + 
	xmlStrlen(item->value) +
	strlen("    <item label=\"\"></item>\n");
      while (item_len > ((items_size - items_len) - 1))
	{
	  items_size += CHUNKSIZE;
	  items_str = (char *)realloc(items_str, items_size);
	  assert(items_str);
	}
      sprintf(&(items_str[items_len]), "    <item label=\"%s\">%s</item>\n",
	      item->label, item->value);
      items_len = strlen(items_str);
    }
  len += items_len;
  len += strlen("  <code>\n</code>\n");
  len += xmlStrlen(agent->code);  
  len += strlen("  <results>\n</results>\n");
  len += xmlStrlen(agent->results);  
  len += strlen("------------0xKhTmLbOuNdArY--\r\n");

#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "username [%d], password [%d], items [%d:%d], code [%d], results [%d], additional [%d], total [%d]\n",
	   xmlStrlen(agent->username),  
	   xmlStrlen(agent->password),  
	   strlen(items_str), items_len,  
	   xmlStrlen(agent->code),  
	   xmlStrlen(agent->results),
	   strlen("------------0xKhTmLbOuNdArY\r\n\
Content-Disposition: form-data\r\n\
Content-Type: text/xml\r\n\
\n\
<agent>\n\
  <sender>\n\
    <user></user>\n\
    <password></password>\n\
  </sender>\n\
  <data></data>\n\
  <code></code>\n\
  <results></results>\n\
</agent>\r\n\
------------0xKhTmLbOuNdArY--\r\n\n"),
	   len);  
#endif

  data = (char *)malloc(len);
  assert(data);
  
  sprintf(data, "\
------------0xKhTmLbOuNdArY\r\n\
Content-Disposition: form-data\r\n\
Content-Type: text/xml\r\n\
\r\n\
<agent>\n\
  <sender>\n\
    <user>%s</user>\n\
    <password>%s</password>\n\
  </sender>\n\
  <data>\n\
%s\
  </data>\n\
  <code>%s</code>\n\
  <results>%s</results>\n\
</agent>\r\n\
------------0xKhTmLbOuNdArY--\r\n", 
	  agent->username, 
	  agent->password, 
	  items_str, 
	  agent->code, 
	  agent->results);

#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "MIME body [%d:%d] %s", 
	   len, strlen(data), data);
#endif

  socket = connectTCP(host, port);
  if (socket < 0)
    {
      Tcl_AppendResult(interp, "ERROR: cannot connect socket in go command\n",
		       (char *)NULL);
      tcl_ret = TCL_ERROR;
      goto end;
    }
      
  write(socket, "POST ", strlen("POST "));
  write(socket, cgiprog, strlen(cgiprog));
  write(socket, " HTTP/1.1\r\n", strlen(" HTTP/1.1\r\n"));
  write(socket, "Host: ", strlen("Host: "));
  write(socket, host, strlen(host));
  write(socket, ":", strlen(":"));
  write(socket, port, strlen(port));
  write(socket, "\r\n", strlen("\r\n"));
  write(socket, "Content-Type: multipart/form-data; boundary=----------0xKhTmLbOuNdArY\r\n", 
	strlen("Content-Type: multipart/form-data; boundary=----------0xKhTmLbOuNdArY\r\n"));
  sprintf(content_len_str, "Content-Length: %d\r\n", (int)strlen(data));
  write(socket, content_len_str, strlen(content_len_str));
  write(socket, "\r\n", strlen("\r\n"));
  write(socket, data, strlen(data));
  shutdown(socket, 1);
#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "request sent:\n%s\n", data);
#endif

  reply_size = CHUNKSIZE;
  reply = (char *)malloc(reply_size);
  assert(reply);
  index = 0;
  c = '\0';

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "starting to read reply");
#endif
    
  while(1)
    {
      ret = read(socket, &c, 1);
      if (ret == EOF || ret == 0)
	{
	  break;
	}
      if (ret < 0)
	{
	  Tcl_AppendResult(interp, 
			   "ERROR: cannot read from socket in go command\n",
			   (char *)NULL);
	  tcl_ret = TCL_ERROR;
	  goto end;
	}
      reply[index] = c;
      index++;
      reply[index] = '\0';
      
      if (index == reply_size - 1)
        {
          reply_size += CHUNKSIZE;
          reply = (char *)realloc(reply, reply_size);
	  assert(reply);
	}
    }
  
#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "server reply is:\n%s\n", reply);
#endif

  reply_body = strstr(reply, "\r\n\r\n");
  if (reply_body == NULL) 
    {
      result = strdup("Error: no reply from server");
    }
  else
    {
      reply_body += strlen("\r\n\r\n");
      result = strdup(reply_body);
    }

  Tcl_SetResult(interp,
		result,
		TCL_VOLATILE);
  
 end:
  if (url != NULL) free(url);
  if (host != NULL) free(host);
  if (proto != NULL) free(proto);
  if (port != NULL) free(port);
  if (cgiprog != NULL) free(cgiprog);
  if (items_str != NULL) free (items_str);
  if (data != NULL) free(data);
  if (reply != NULL) free(reply);

  return tcl_ret;

} /* go Command */

int main(int argc, char* argv[], char *env[])
{
  char c;
  char data[AGENTMAXSIZE];
  int data_len;
  int ret;
  char dirname[DIRSIZE];
  char dircommand[DIRSIZE];
  char *xml_data = NULL;
  char *xml_data_ptr = NULL;
  unsigned long xml_data_len;
  struct agent_descr *agent = NULL;
  xmlDocPtr doc;
  xmlNodePtr root;
  xmlNodePtr cur;
  xmlNodePtr sub;
  struct data_item *item = NULL;
  Tcl_Interp *interp = NULL;
  struct stat sb;

#ifdef DEBUG2
  int i;
  xmlChar *debug_str;
  int debug_len;
#endif


#ifdef DEBUG2
  i = 0;
  while(env[i] != NULL)
    {
      my_debug(__FILE__, __LINE__, "%s", env[i]);
      i++;
    }
#endif

  data_len = 0;
  while (1)
    {
      ret = read(0, &c, 1);
      if (ret == 0)
	{
	  break;
	}
      if (ret < 0)
	{
	  send_reply(MSG_ERR_READ);
	  exit(1);
	}
      data[data_len] = c;
      data_len++;
      data[data_len] = '\0';
    }

#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "data is %s", data);
#endif

  xml_data = strstr(data, AGENT_START_TAG);

  if (xml_data == NULL)
    {
      send_reply(MSG_ERR_NODATA); 
      exit(1);
    }

  xml_data_ptr = strstr(xml_data, AGENT_END_TAG);

  if (xml_data_ptr == NULL)
    {
      send_reply(MSG_ERR_NODATA); 
      exit(1);
    }
  
  xml_data_ptr += strlen(AGENT_END_TAG);
  xml_data_len = xml_data_ptr - xml_data;
  
#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "data length is %d", xml_data_len);
#endif

  doc = xmlParseMemory(xml_data, xml_data_len); 

  if (doc == NULL)
    {
      my_error(__FILE__, __LINE__, "null agent document");
      send_reply(MSG_ERR_PARSE);
      exit(1);
    }

  root = xmlDocGetRootElement(doc);

  if (root == NULL)
    {
      my_error(__FILE__, __LINE__, "null agent root element");
      send_reply(MSG_ERR_PARSE);
      exit(1);
    }

#ifdef DEBUG2
  xmlDocDumpMemory(doc, &debug_str, &debug_len);
  if (debug_str == NULL)
    {
      send_reply(MSG_ERR_PARSE);
      exit(1);
    }
  my_debug(__FILE__, __LINE__, "agent is %s", (char *)debug_str);
  xmlFree(debug_str);
#endif

  if (xmlStrcmp(root->name, (const xmlChar *)"agent"))
    {
      send_reply(MSG_ERR_PARSE);
      exit(1);
    }

  agent = (struct agent_descr *)malloc(sizeof(struct agent_descr));
  assert(agent);
  bzero(agent, sizeof(struct agent_descr));
  agent->data.next = agent->data.prev = &(agent->data);

  cur = root->xmlChildrenNode;

  while (cur != NULL)
    {
      assert(cur->name);
      
      if (!(xmlStrcmp(cur->name, (const xmlChar *)"sender")))
	{
	  sub = cur->xmlChildrenNode;
	  while(sub != NULL)
	    {
	      if (!(xmlStrcmp(sub->name, (const xmlChar *)"user")))
		{
		  agent->username = xmlNodeListGetString(doc, sub->xmlChildrenNode, 1);
		}
	      else if (!(xmlStrcmp(sub->name, (const xmlChar *)"password")))
		{
		  agent->password = xmlNodeListGetString(doc, sub->xmlChildrenNode, 1);
		}
	      else if (!(xmlStrcmp(sub->name, (const xmlChar *)"text")))
		{
		  /* do nothing */
		}
	      else 
		{
		  my_error(__FILE__, __LINE__, "unknown element %s", sub->name);
		  send_reply(MSG_ERR_PARSE);
		  exit(1);
		}

	      sub = sub->next;
	    }
	  
	}
      else if (!(xmlStrcmp(cur->name, (const xmlChar *)"data")))
	{
	  sub = cur->xmlChildrenNode;
	  while(sub != NULL)
	    {
	      if (!(xmlStrcmp(sub->name, (const xmlChar *)"item")))
		{
		  item = malloc(sizeof(struct data_item));
		  assert(item);
		  item->label = xmlGetProp(sub, (const xmlChar *)"label");
		  if (item->label == NULL)
		    {
		      send_reply(MSG_ERR_PARSE);
		      exit(1);
		    }
		  item->value = xmlNodeListGetString(doc, sub->xmlChildrenNode, 1);
		  if (item->value == NULL)
		    {
		      send_reply(MSG_ERR_PARSE);
		      exit(1);
		    }
		  item->next = &(agent->data);
		  item->prev= agent->data.prev; 
		  agent->data.prev = item;
		  item->prev->next = item;
		}
	      else if (!(xmlStrcmp(sub->name, (const xmlChar *)"text")))
		{
		  /* do nothing */
		}
	      else 
		{
		  my_error(__FILE__, __LINE__, "unknown element %s", sub->name);
		  send_reply(MSG_ERR_PARSE);
		  exit(1);
		}

	      sub = sub->next;
	    }
	
	}
      else if (!(xmlStrcmp(cur->name, (const xmlChar *)"code")))
	{
	  agent->code = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1);
	  if (agent->code == NULL)
	    {
	      send_reply(MSG_ERR_PARSE);
	      exit(1);
	    }
	}
      else if (!(xmlStrcmp(cur->name, (const xmlChar *)"results")))
	{
	  agent->results = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1);
	}
      else if (!(xmlStrcmp(cur->name, (const xmlChar *)"text")))
	{
	  /* do nothing */
	}
      else
	{
	  my_error(__FILE__, __LINE__, "unknown element %s", cur->name);
	  send_reply(MSG_ERR_PARSE);
	  exit(1);
	}
      
      cur = cur->next;
    }
  

  if ((agent->username == NULL) || (agent->password == NULL)) 
    {
      my_error(__FILE__, __LINE__, "empty username or password");
      send_reply(MSG_ERR_PARSE);
      exit(1);
    }
  
  interp = Tcl_CreateInterp();
  assert(interp);
  Tcl_MakeSafe(interp);

  /* Register commands */
  Tcl_CreateCommand(interp,
		    "go",
		    (Tcl_CmdProc*)GoCommand,
		    (ClientData) agent,
		    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp,
		    "data",
		    (Tcl_CmdProc*)DataCommand,
		    (ClientData) agent,
		    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp,
		    "store",
		    (Tcl_CmdProc*)StoreCommand,
		    (ClientData) agent,
		    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp,
		    "results",
		    (Tcl_CmdProc*)ResultsCommand,
		    (ClientData) agent,
		    (Tcl_CmdDeleteProc *)NULL);
  
#ifdef DEBUG2
  my_debug(__FILE__, __LINE__, "starting Tcl interpreter for [%s]", 
	(char*)agent->code);
#endif

  /* Check if username/password combo exists */
  sprintf(dirname, "%s:%s", agent->username, agent->password);
  if (stat(dirname, &sb)) 
    {
      sprintf(dircommand, "mkdir %s:%s", agent->username, agent->password);
      system(dircommand);
    }
  chdir(dirname);

  ret = Tcl_Eval(interp, (char *)agent->code);
  
#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "Tcl interpreter terminated (%d)", ret);
#endif

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "Sending results (%s)", (char *)agent->results);
#endif

  if (ret == TCL_OK)
    {
      send_reply((char *)agent->results); 
    }
  else
    {
      send_reply((char *)Tcl_GetStringResult(interp)); 
    }
  fflush(stdout);

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "Results sent, exiting");
#endif

  exit(0);
}
