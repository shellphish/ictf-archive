#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

int getIntParam(char *p) {
    char buffer[5];
    int value;

    strncpy(buffer, p, 2);
    buffer[2] = '\0';
    value = strtol(buffer, 0x0, 16);
    return value;
}

void executeCommand(char *command) {
  int debug = 1;

  if (debug) {
    printf("executing [%s]\n", command);
  }

  system(command);
}

int main(int argc, char **argv) {
  char *ip = argv[1];
  char *flag = argv[2];
  char *adminPassword = argv[3];

  int i;
  int params[32];
  char preamble[512];
  char *adminLogin = "admin";
  char request[512];
  char command[512];

  if (argc == 1) {
    printf("usage: %s <ip> <flag> <passwd>\n", argv[0]);
    exit(1);
  }

  sprintf(preamble, "http://%s:8000/admin", ip);

  for (i = 0; i < 16; i++) {
    params[i] = getIntParam(flag+(2*i));
    // printf("params[%i] = %i\n", i, params[i]);
  }

  

  // set #0
  //  http://128.111.48.5:8000/admin/fallbacks?mount=/ices&id=1&int=13&limit=123&halt=255

  sprintf(request, 
	  "%s/fallbacks?mount=ices&fbindex1=%i&fbindex2=%i", 
	  preamble,
	  params[0],
	  params[1]);

  sprintf(command, "wget -T 10 -O /dev/null --http-user=%s --http-passwd=%s --quiet \"%s\"", 
	  adminLogin,
	  adminPassword,
	  request);

  executeCommand(command);

  // http://128.111.48.5:8000/admin/metadata?mount=/ices&mode=1&song=2&id=1&int=13&limit=123&halt=255

  sprintf(request, 
	  "%s/metadata?mount=/ices&mode=1&song=Intro&id=%i&int=%i&limit=%i&halt=%i", 
	  preamble,
	  params[2],
	  params[3],
	  params[4],
	  params[5]);

  sprintf(command, "wget -T 10 -O /dev/null --http-user=%s --http-passwd=%s --quiet \"%s\"", 
	  adminLogin,
	  adminPassword,
	  request);

  executeCommand(command);



  // http://128.111.48.5:8000/admin/listclients?mount=/ices&service=1&streamid=2&minduration=1&maxduration=255

  sprintf(request, 
	  "%s/listclients?mount=/ices&service=%i&streamid=%i&minduration=%i&maxduration=%i", 
	  preamble,
	  params[6],
	  params[7],
	  params[8],
	  params[9]);

  sprintf(command, "wget -T 10 -O /dev/null --http-user=%s --http-passwd=%s --quiet \"%s\"", 
	  adminLogin,
	  adminPassword,
	  request);

  executeCommand(command);



  // http://128.111.48.5:8000/admin/streamlist?streamid=2&format=1&intlimit=255&extlimit=255

  sprintf(request, 
	  "%s/streamlist?streamid=%i&format=%i&intlimit=%i&extlimit=%i", 
	  preamble,
	  params[10],
	  params[11],
	  params[12],
	  params[13]);

  sprintf(command, "wget -T 10 -O /dev/null --http-user=%s --http-passwd=%s --quiet \"%s\"", 
	  adminLogin,
	  adminPassword,
	  request);

  executeCommand(command);


  // http://128.111.48.5:8000/admin/killclient?mount=/ices&id=21&sourceid=12&errormsg=23  
  
  sprintf(request, 
	  "%s/killclient?mount=/ices&id=42&sourceid=%i&errormsg=%i", 
	  preamble,
	  params[14],
	  params[15]);

  sprintf(command, "wget -T 10 -O /dev/null --http-user=%s --http-passwd=%s --quiet \"%s\"", 
	  adminLogin,
	  adminPassword,
	  request);

  executeCommand(command);

}
