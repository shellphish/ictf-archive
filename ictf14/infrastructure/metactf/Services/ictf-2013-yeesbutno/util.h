/*********************************************************************
 * @file          util.h
 * @version
 * @brief
 * @author        badnack <n.redini@gmail.com>
 * @date          Tue Dec  3 23:09:56 2013
 * Modified at:   Thu Dec  5 21:10:48 2013
 * Modified by:   badnack <n.redini@gmail.com>
 ********************************************************************/

#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <string>

#include "userdb.h"

#ifndef __UTIL_H__
#define __UTIL_H__

#define LISTEN_POOL 50
#define EPOCH_INTERVAL 600
#define EPOCHS (3600 / EPOCH_INTERVAL) * 8
#define END_STR "\n\r"
#define CLEANER_SLEEP 2 * EPOCH_INTERVAL
#define CLEANER_THRESH EPOCH_INTERVAL
#define MOVEMENT_LIMIT 128
#define READ_BUF_LIMIT 1024
#define KEY_SIZE 1024

typedef struct thread_arg thread_arg;
struct thread_arg{
  int id;
  int sock;
  int epoch_n;
  dbentry *cred;
};

char* recv_str(thread_arg *);
void set_init_epoch();
int get_current_epoch();

extern int starting_epoch;
extern unsigned char master_hash[];
#endif
