/*********************************************************************
 * @file          userdb.c
 * @version
 * @brief
 * @author        badnack <n.redini@gmail.com>
 * @date          Wed Dec  4 09:56:26 2013
 * Modified at:   Wed Dec  4 10:19:12 2013
 * Modified by:   badnack <n.redini@gmail.com>
 ********************************************************************/
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <openssl/sha.h>

#include "userdb.h"

unsigned int uid = 0 ;
hash_table *ht;
unsigned long long int mt [DIGIT_HASH];
dbentry *oldest = NULL, *newest = NULL;
int db_size = 0;
pthread_mutex_t dblock = PTHREAD_MUTEX_INITIALIZER;


int
init_db()
{
  int i = 0;
  if ((ht = (hash_table*) calloc(HASH_SIZE, sizeof(hash_table))) == NULL) {
    return -1;
  }

  for  (i = 0; i < HASH_SIZE; i++) {
    ht[i].size = 0;
    ht[i].head = NULL;
    ht[i].last = NULL;
  }

  // creating the table to hash indexes
  mt[0] = 1;
  for (i = 1; i < DIGIT_HASH; i++) {
    mt[i] = (256 * mt[i - 1]) % HASH_SIZE;
  }

  return 0;
}


unsigned int
get_hash(char *username)
{
  char tmp [(MAX_USER_CHAR * 2) + 1];
  unsigned char sha_buf[20];
  unsigned int index;
  int len, i;

  strncpy(tmp, username, MAX_USER_CHAR);
  len = strlen(tmp);

  SHA1((unsigned char*)tmp, len, sha_buf);

  index = 0;
  for (i = 0; i < DIGIT_HASH; i++) {
    index += (int)(sha_buf[i] * mt[i]);
  }
  index %= HASH_SIZE;

  return index;
}

// void
// print_list()
// {
//   int i = 0, j = 0;
//   dbentry *tmp;

//   fprintf(stderr, "list: \n");
//   for (i = 0; i < HASH_SIZE; i++) {
//     tmp = ht[i].head;
//     if (tmp == NULL) {
//       continue;
//     }

//     fprintf(stderr, "%i)", i);
//     for (j = 0; j < ht[i].size; j++) {
//       fprintf(stderr, " %s ->", tmp->username);
//       tmp = tmp->h_next;
//     }
//     fprintf(stderr, "\n");
//   }

//   fprintf(stderr, "Timing: \n");
//   tmp = oldest;
//   while (tmp != NULL) {
//     fprintf(stderr, "%s ->", tmp->username);
//     tmp = tmp->t_next;
//   }
//   return ;
// }

int
add_user(char *username, char *password, char *secret, dbentry **cred)
{
  int i;
  unsigned int index;
  dbentry *entry, *tmp;

  pthread_mutex_lock(&dblock);
  index = get_hash(username);

  tmp = ht[index].head;

  for (i = 0; i < ht[index].size; i++) {
    if (!strncmp(tmp->username, username, MAX_USER_CHAR)) {
      pthread_mutex_unlock(&dblock);
      return GEN_ERROR;
    }
    tmp = tmp->h_next;
  }

  if (ht[index].head == NULL) {
    if ((ht[index].head = (dbentry*) malloc(sizeof(dbentry))) == NULL) {
      pthread_mutex_unlock(&dblock);
      return GEN_ERROR;
    }
    ht[index].last = ht[index].head;
    ht[index].last->h_next = NULL;
  } else {
    if ((ht[index].last->h_next = (dbentry*) malloc(sizeof(dbentry))) == NULL) {
      pthread_mutex_unlock(&dblock);
      return GEN_ERROR;
    }
    tmp = ht[index].last->h_next;
    tmp->h_next = NULL;
    ht[index].last = tmp;
  }

  ht[index].size++;
  entry = ht[index].last;
  if (oldest == NULL) {
    oldest = entry;
    newest = entry;
  } else {
    newest->t_next = entry;
    newest = entry;
  }

  strncpy(entry->username, username, MAX_USER_CHAR);
  strncpy(entry->password, password, MAX_USER_CHAR);
  strncpy(entry->secret, secret, MAX_USER_CHAR);
  entry->id = ++uid;
  entry->time_stamp = time(NULL);
  entry->h_next = NULL;
  entry->t_next = NULL;

  *cred = (dbentry*) malloc(sizeof(dbentry));
  strncpy((*cred)->username, username, MAX_USER_CHAR);
  strncpy((*cred)->password, password, MAX_USER_CHAR);
  strncpy((*cred)->secret, secret, MAX_USER_CHAR);
  (*cred)->id = entry->id;
  (*cred)->time_stamp = entry->time_stamp;
  (*cred)->h_next = NULL;
  (*cred)->t_next = NULL;

  pthread_mutex_unlock(&dblock);

  return OK;
}


int
check_cred(char *username, char *password, dbentry **cred)
{
  int i, res;
  unsigned int index;
  dbentry * tmp;

  res = NO_ENTRY;

  pthread_mutex_lock(&dblock);
  index = get_hash(username);
  tmp = ht[index].head;

  for (i = 0; i < ht[index].size; i++) {
    if (!strncmp(tmp->username, username, MAX_USER_CHAR)) {
      if (!strncmp(tmp->password, password, MAX_USER_CHAR)) {
        if ((*cred = (dbentry*) malloc(sizeof(dbentry))) == NULL) {
          res = GEN_ERROR;
          break;
        }
        strncpy((*cred)->username, tmp->username, MAX_USER_CHAR);
        strncpy((*cred)->password, tmp->password, MAX_USER_CHAR);
        strncpy((*cred)->secret, tmp->secret, MAX_USER_CHAR);
        (*cred)->time_stamp = tmp->time_stamp;
        (*cred)->id = tmp->id;
        (*cred)->h_next = (*cred)->t_next = NULL;
        res = OK;
      } else {
        res = WRONG_CRED;
        *cred = NULL;
      }
      break;
    }
    tmp = tmp->h_next;
  }

  pthread_mutex_unlock(&dblock);
  return res;
}

void
remove_older_than(int sec)
{
  dbentry *tmp;
  int index;
  time_t now;

  now = time(NULL);
  pthread_mutex_lock(&dblock);

  while (oldest != NULL && (now - oldest->time_stamp) > sec) {
    index = get_hash(oldest->username);
    ht[index].head = oldest->h_next;
    ht[index].size--;
    tmp = oldest;
    oldest = oldest->t_next;
    free(tmp);
  }
  pthread_mutex_unlock(&dblock);
}

dbentry*
get_user_cred(char* username)
{
  int index, i;
  dbentry *tmp, *ret;

  pthread_mutex_lock(&dblock);
  index = get_hash(username);
  tmp = ht[index].head;
  ret = NULL;

  for (i = 0; i < ht[index].size; i++) {
    if (!strncmp(tmp->username, username, MAX_USER_CHAR)) {
      ret = tmp;
      break;
    }
    tmp = tmp->h_next;
  }
  pthread_mutex_unlock(&dblock);

  return ret;
}
