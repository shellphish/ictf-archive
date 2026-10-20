//====================================================================
// @file          screens.cpp
// @version
// @brief
// @author        badnack <n.redini@gmail.com>
// @date          Wed Dec  4 10:23:37 2013
// Modified at:   Fri Dec  6 00:07:51 2013
// Modified by:   badnack <n.redini@gmail.com>
//====================================================================
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>

#include "screens.h"
#include "userdb.h"

int
cred_screen(thread_arg *ta)
{
  char s_init [1024];
  char s_pass [] = "Insert Password: ";
  char s_secret [] = "No user present in DB found. Insert a secret to register: ";
  char *username, *password, *secret;
  int c_ret;

  secret = NULL;

  //FIXME: your epoch is.. is too general!
  sprintf(s_init, "Your epoch is: %i.\nInsert Username: ", ta->epoch_n);

  // Receive Username
  if (send(ta->sock, s_init, strlen(s_init), MSG_NOSIGNAL) < 1) {
    return -1;
  }

  if ((username = recv_str(ta)) == NULL) {
    return -1;
  }

  // Receive password
  if (send(ta->sock, s_pass, strlen(s_pass), MSG_NOSIGNAL) < 1) {
    return -1;
  }
  if ((password = recv_str(ta)) == NULL) {
    free(username);
    return -1;
  }


  // Try to login with that credentials
  c_ret = check_cred(username, password, &ta->cred);
  if (c_ret<0)
  {
    // No user present into the db, ask for secret
    if (send(ta->sock, s_secret, strlen(s_secret), MSG_NOSIGNAL) < 1) {
      free(username);
      free(password);
      return -1;
    }

    if ((secret = recv_str(ta)) == NULL) {
      free(username);
      free(password);
      return -1;
    }
    
    // If somthing has gone wrong with registration, return
    if (!strnlen(secret, MAX_USER_CHAR)) {

      if (secret != NULL) {
        free(secret);
      }
      free(username);
      free(password);
      return c_ret;
    }    
    
    // registration
    c_ret = add_user(username, password, secret, &ta->cred);
    free(username);
    free(password);
    if (secret != NULL) {
      free(secret);
    }
  }

  return (c_ret == OK) ? 0 : -1;
}


int
menu_screen(thread_arg *ta)
{
  char choose[] = "Do you want to (p)lay.\nDo you want to see your (s)ecret\n?>";
  char *dec;

  if (send(ta->sock, choose, strlen(choose), MSG_NOSIGNAL) < 1) {
    return -1;
  }
  if ((dec = recv_str(ta)) == NULL) {
    return -1;
  }
  if (strlen(dec) > 1) {
    free(dec);
    return -1;
  }

  if (dec[0] == 's') {
    free(dec);
    return 0;
  }
  else if (dec[0] == 'p') {
    free(dec);
    return 1;
  }
  free(dec);
  return -1;
}

int
send_secret(thread_arg *ta)
{
  if (send(ta->sock, ta->cred->secret, strlen(ta->cred->secret), MSG_NOSIGNAL) < 1) {
    return -1;
  }
  return 0;
}

int
entry_screen(thread_arg * ta)
{
  char q [] = "Which user\'s secret are you looking for?\n?>";
  char *r;
  dbentry *entry;

  if (send(ta->sock, q, strlen(q), MSG_NOSIGNAL) < 1) {
    return -1;
  }

  if ((r = recv_str(ta)) == NULL) {
    return -1;
  }

  if ((entry = get_user_cred(r)) == NULL) {
    return -1;
  }

  if (send(ta->sock, entry->secret, strlen(entry->secret), MSG_NOSIGNAL)) {
    return -1;
  }

  return 0;
}
