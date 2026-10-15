#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

char msg[] = 
    #include "story.txt"
    "\n";

void usleep(long n)
{
    int factor = 10;
    long i;
    for (i = 0; i < factor * n; i++)
        ;
}

int
main(void)
{

   int i;
   /*struct timeval tm;*/
   int rdelay; 
   int nlines = 0;
   int user = 0;

   close(0);
   close(2);

   signal(SIGINT, SIG_IGN);
   signal(SIGTERM, SIG_IGN);

   /*gettimeofday(&tm, NULL);*/
   /*srand(tm.tv_sec ^ tm.tv_usec);*/
   srand(42);

   for (i = 0; i < strlen(msg); i++) {
      printf("%c", msg[i]); 
      fflush(stdout);

      if (user) {
//         printf("user = 1\n");
         rdelay = 500 + (int) (150000.0 * (rand() / (RAND_MAX + 500.0)));      
      }
      else {
//         printf("user = 0\n");
         rdelay = 0;
      }
      //usleep(rdelay + 50000);
      usleep(500000);

      if (msg[i] == '\n') {
         usleep(500000);
         if (++nlines == 2) {
            if (!user)
               user = 1;
            else
               user = 0;
            nlines = 0;
         }
      }
      else 
         nlines = 0;
   }

   printf("\n\n");
   sleep(3);


   for (i = 10; i >= 0; i--) 
   {
       printf("WARNING: THIS MACHINE WILL SELF-DESTROY IN %d SECONDS...\r", i);
       fflush(stdout);
       sleep(1);
   }

   unlink("\kernel.sys");

   //system("\fdos\bin\fdapm warmboot");

   return 0;
}
