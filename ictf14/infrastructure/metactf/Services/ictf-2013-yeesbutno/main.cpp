//====================================================================
// @file          main.cpp
// @version
// @brief
// @author        badnack <n.redini@gmail.com>
// @date          Tue Dec  3 23:09:40 2013
// Modified at:   Thu Dec  5 22:30:24 2013
// Modified by:   badnack <n.redini@gmail.com>
//====================================================================
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <pthread.h>
#include <signal.h>

#include "userdb.h"
#include "util.h"
#include "screens.h"
#include "read_movement.h"
#include "ubersecurecrypt.h"

int listensd;

//FIXME CHECK mallocs if they are freed everytime!



void
kill_handler(int v)
{
  close(listensd);
  exit(0);
}

void*
execute_service(void* va)
{
  thread_arg* ta = (thread_arg*) va;
  char data [MOVEMENT_LIMIT];
  int choose, len;
  unsigned char udata [MOVEMENT_LIMIT];
  unsigned int ulen;

  // Skip the first since it is hardcoded!
  ta->epoch_n = get_current_epoch() + 1;

  // login or register
  if (!cred_screen(ta)) {
    // main menu
    choose = menu_screen(ta);
    // game
    if (choose == 1) 
    {
      fprintf(stderr,"\nCHOOSEN 0\n");
      if (read_moves(*ta, data, &len) && !(len % 4)) 
      {
	convert_moves_to_buffer(data, len, udata, &ulen);
	if (is_it_valid(master_hash, 16, udata, ulen, ta->epoch_n)) 
        {
	  entry_screen(ta);
	}
      }
    }
    else if (choose==0)
    {
      fprintf(stderr,"\nCHOOSEN 0\n");
      send_secret(ta);
    }
    else
    {
      close(ta->sock);
      if (ta->cred) {
        free(ta->cred);
      }
      free(ta);
      fprintf(stderr, "Client has disconnected\n");

      return NULL;
    }
    
  }

  close(ta->sock);
  if (ta->cred) {
    free(ta->cred);
  }
  free(ta);
  fprintf(stderr, "Client has disconnected\n");

  return NULL;
}

void*
execute_cleaner(void* v)
{
  while (1) {
    sleep(CLEANER_SLEEP);
    remove_older_than(CLEANER_THRESH);
    // print_list();
  }

  return NULL;
}

int
main(int argc, char *argv[])
{
  int listensd, clientsd;
  int reuse, id, v;
  socklen_t clilen;
  pthread_t t, c;
  thread_arg *ta;
  struct timeval timeout;
  struct sockaddr_in server_addr, client_addr;

  if (argc <= 1) {
    fprintf(stderr, "Usage: %s [port]\n", argv[0]);
    exit(-1);
  }

  reuse = 1;
  id = 0;

  init_db();
  set_init_epoch();

  signal(SIGKILL, kill_handler);
  signal(SIGINT, kill_handler);
  signal(SIGQUIT, kill_handler);

  if (pthread_create(&c, NULL, execute_cleaner, (void*) &v)) {
    perror("Cannot create another thread\n");
    exit(-1);
  }

  if ((listensd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    perror("Error in creating a new socket");
    exit(2);
  }

  if (setsockopt(listensd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) == -1) {
    perror("setsockopt error");
    exit(1);
  }
  
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
  server_addr.sin_port = htons(atoi(argv[1]));

  if (bind(listensd, (struct sockaddr*) &server_addr, sizeof(server_addr)) < 0) {
    perror("Error in binding a new socket");
    exit(-1);
  }

  if (listen(listensd, LISTEN_POOL)) {
    perror("Error on listen");
    exit(-1);
  }

  timeout.tv_sec = 10;
  timeout.tv_usec = 0;

  while (1) {
    clilen = sizeof(client_addr);
    if ((clientsd = accept(listensd, (struct sockaddr*) &client_addr, &clilen)) == -1) {
      perror("Fork has failed, connection has been dropped\n");
      sleep(1);
      continue;
    }
    if (setsockopt (clientsd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)) < 0) {
      perror("setsockopt failed\n");
    }
    ta = (thread_arg*) malloc(sizeof(thread_arg));
    ta->sock = clientsd;
    ta->id = ++id;
    ta->cred = NULL;

    if (pthread_create(&t, NULL, execute_service, (void*) ta)) {
      perror("Cannot create another thread\n");
      sleep(1);
      continue;
    }
    pthread_detach(t);
  }

}
