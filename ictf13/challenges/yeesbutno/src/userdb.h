/*********************************************************************
 * @file          userdb.h
 * @version
 * @brief
 * @author        badnack <n.redini@gmail.com>
 * @date          Wed Dec  4 09:56:20 2013
 * Modified at:   Fri Dec  6 02:33:20 2013
 * Modified by:   badnack <n.redini@gmail.com>
 ********************************************************************/
#include <time.h>

#ifndef __USERDB_H
#define __USERDB_H

#define MAX_USER_CHAR 1024
#define HASH_SIZE 1024
#define DIGIT_HASH 4

typedef struct dbentry dbentry;
struct dbentry {
  time_t time_stamp;
  unsigned int id;
  char username [MAX_USER_CHAR + 1];
  char password [MAX_USER_CHAR + 1];
  char secret [MAX_USER_CHAR + 1];
  dbentry *h_next; //hashing table next
  dbentry *t_next; //timing next
};

typedef struct hash_table hash_table;
struct hash_table {
  int size;
  dbentry *head;
  dbentry *last;
};

enum {
  OK         =  0,
  NO_ENTRY   = -1,
  WRONG_CRED = -2,
  GEN_ERROR  = -3
};

extern hash_table * ht;

int init_db();
void clean_db();
int add_user(char *, char *, char *, dbentry **);
int check_cred(char *, char *, dbentry **);
void remove_older_than(int);
dbentry* get_user_cred(char*);

#endif
