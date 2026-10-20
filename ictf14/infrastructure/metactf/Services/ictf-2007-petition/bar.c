#include <stdio.h>

int main(int argc, char* argv[]) {
  FILE *f = NULL;
  unsigned char c;

  if (argv[1] == NULL) return -1;

  f = fopen(argv[1], "r");        	
  if (f == NULL) {
    fprintf(stderr, "Can't open file %s\n", argv[2]);
    return -1;
  }
  printf("char code[] = \"");
  while (fread(&c, 1, 1, f)) {
    printf("\\x%02x", c);
  }
  printf("\";\n");
  fclose(f);
  return 0;
}  
  
