#include "read_movement.h"

void joke_the_user(void)
{
  return;
}

bool parse_attack(char* str, int max, char* err_buff, int max_out_buff)
{
  int i=0;
  int index=-1;
  int semicolon_index=-1;

  err_buff[0]='\0';
  // Look fro a quote or a double quote
  while (i<max)
    {
      if (str[i]=='\'' || str[i]=='\"')
        {
          index=i;
          break;
        }
      i++;
    }


  if (index!=-1)
    {
      // Now look for semi-colon
      for (i=index;i<max;i++)
        {
          if (str[i]==';')
            {
              semicolon_index=i;
              break;
            }
        }
    }

  // If the attempt is good, populate the error message and return true
  if (index!=-1 && semicolon_index!=-1)
    {
      strncpy(err_buff,str+semicolon_index,max_out_buff);
      return true;
    }
  else
    return false;

}

/*
  This function will read up to MOVEMENT_LIMIT mvoes from the socket.
  All the movement will be stored into moves pointed array. So please
  allocate a char[MOVEMENT_LIMIT] array from the caller and pass a
  pointer to it.
  If an attack has been detected or an error happens, it will return
  false; otherwise true is returned.
*/
bool read_moves(thread_arg arg, char* moves, int *n)
{
  char obuff[20];
  char s[READ_BUF_LIMIT];
  int i=0, read_bytes,j=0;
  int east=0;
  int north=0;
  unsigned int t = 0;
  int b = 0;
  int comb[2];
  unsigned int k=0;
  void(*discover_function)(void);
  const char* discover_message;
  char* nilo = NULL;

  *n=0;
  moves[0]='\0';

  while (i<MOVEMENT_LIMIT)
    {
      if (send(arg.sock, NEXT_MOVEMENT, strlen(NEXT_MOVEMENT),MSG_NOSIGNAL)<1)
        {
          perror("Error on send.");
          return false;
        }
      //fprintf(stderr,"Receiving data...");
      discover_function = NULL;

      // Read the char and add to the array
      if (nilo != NULL) {
        free(nilo);
      }
      
      nilo = recv_str(&arg);
      if (nilo==NULL)
      {
        *n=0;
        return false;
      }

      b = strlen(nilo);
      // If a regular movement has been detected, increase the counter and send some
      // info to the client
      if (b == 1)
        {
          // Check if the character is good
          switch (nilo[0])
            {
            case 'e':
              ++east;
              break;
            case 'n':
              ++north;
              break;
            case 'w':
              --east;
              break;
            case 's':
              --north;
              break;
            default:
              // Error detected. Not a valid movement.
              if (send(arg.sock,INVALID_MOVEMENT,strlen(INVALID_MOVEMENT),MSG_NOSIGNAL)<1)
                {
                  perror("Error on send.");
                  if (nilo != NULL) {
                    free(nilo);
                  }
                  return false;
                }
              continue;
            }

          t = time(NULL);
          t = t / EPOCH_INTERVAL;
          // Choose the message from the table
          comb[0]=north;
          comb[1]=east;
          SHA1((unsigned char*)comb, sizeof(int)*2, (unsigned char*)obuff);
          j = (*(unsigned int*)obuff)%100;
          if (j<0)
            j=-j;
          for (k=0;k<sizeof(PROBABILITIES)/sizeof(int);k++)
            {
              //fprintf(stderr,"\nJ:%d, Pk:%d, P(K+1): %d \n",j,PROBABILITIES[k],PROBABILITIES[k+1]);    
              if (k==(sizeof(PROBABILITIES)/sizeof(int)-1))
                {
                  discover_function=DISCOVER_FUNCTIONS[k];
                  discover_message=DISCOVER_MESSAGES[k];
                  break;
                }
              else if (j>=PROBABILITIES[k] && j<=PROBABILITIES[k+1])
                {
                  discover_function=DISCOVER_FUNCTIONS[k];
                  discover_message=DISCOVER_MESSAGES[k];
                  break;
                }
            }
          if (discover_function!=NULL)
            discover_function();
          if( send(arg.sock, discover_message,strlen(discover_message),MSG_NOSIGNAL) <1)
            {
              perror("Error on send.");
              if (nilo != NULL) {
                free(nilo);
              }
              return false;
            }
          moves[i]=nilo[0];
          ++i;
        }
      // If I read more than 1 single byte, call the parser
      else if (b>1)
        {
          //fprintf(stderr,"\nCHECKING FOR EXPLOIT ATTEMPT...\n");
          if (parse_attack(nilo,READ_BUF_LIMIT,s,READ_BUF_LIMIT))
            {
              //fprintf(stderr,"\nATTACKED...\n");
              // Send bullshits to client, then return.
              if (send(arg.sock,SQL_FAKE_ERR,strlen(SQL_FAKE_ERR),MSG_NOSIGNAL)<1)
                {
                  perror("Error on send.");
                  if (nilo != NULL) {
                    free(nilo);
                  }
                  return false;
                }

              if(send(arg.sock,s,strnlen(s,READ_BUF_LIMIT),MSG_NOSIGNAL)<1)
                {
                  perror("Error on send.");
                  if (nilo != NULL) {
                    free(nilo);
                  }
                  
                  return false;
                }
              *n = i;
              if (nilo != NULL) {
                free(nilo);
              }

              return false;
            }
          else
            {
              //fprintf(stderr,"\nNOT ATTACKED...\n");
              if (send(arg.sock,INVALID_MOVEMENT,strlen(INVALID_MOVEMENT),MSG_NOSIGNAL)<1)
                {
                  perror("Error on send.");
                  if (nilo != NULL) {
                    free(nilo);
                  }

                  return false;
                }
              continue;
            }
        }
      else
        {
          // Somthing has gone wrong, return false
          *n = i;
          fprintf(stdout, "\nReceive has failed.\n");
          if (nilo != NULL) {
            free(nilo);
          }
          
          return false;
        }
    }
  *n = i;
  if (nilo != NULL) {
    free(nilo);
  }
  
  return true;
}
