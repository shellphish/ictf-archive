//====================================================================
// @file          util.cpp
// @version
// @brief
// @author        badnack <n.redini@gmail.com>
// @date          Wed Dec  4 10:31:54 2013
// Modified at:   Fri Dec  6 03:52:20 2013
// Modified by:   badnack <n.redini@gmail.com>
//====================================================================
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>

#include "util.h"
#include "userdb.h"

int starting_epoch;

unsigned char master_hash[] = "\x50\x43\x0e\xd3\x9b\x28\xda\xe2\x5a\xa2\xe9\x8b\x4b\x91\x07\xb5";

void
set_init_epoch()
{
  //FIXME: USE THIS!!!
  starting_epoch =  1386316800;
  //starting_epoch = 1386306840;
}

int
get_current_epoch()
{
  return rand() % 500;
}

char*
recv_str(thread_arg *ta)
{
  int count, ret;
  char * data;
  char tmp;

  data = (char*) calloc((MAX_USER_CHAR + 1), sizeof(char));
  count = 0;

  while (count < MAX_USER_CHAR) {
    if ((ret = recv(ta->sock, &tmp, sizeof(char), 0)) <= 0) {
      free(data);
      return NULL;
    }

    if (tmp == END_STR[0] || tmp == END_STR[1]) {
      break;
    }

    data[count] = tmp;
    count += ret;
  }
  data[count] = '\0';
  return data;
}
