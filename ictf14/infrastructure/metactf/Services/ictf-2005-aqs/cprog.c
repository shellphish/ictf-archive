#include <stdio.h>
#include <stdlib.h>

__asm__(
   "speedup:\n\t"
   "push   %ebp\n\t"
   "mov    %esp,%ebp\n\t"
   "sub    $0xc,%esp\n\t"
   "movl   $0x1,0xfffffffc(%ebp)\n\t"
   "mov    0x8(%ebp),%eax\n\t"
   "cmpb   $0x0,(%eax)\n\t"
   "jne    speedup+0x17 \n\t"
   "jmp    speedup+0x5c \n\t"
   "mov    0x8(%ebp),%ecx\n\t"
   "mov    0x8(%ebp),%edx\n\t"
   "movzbl 0xfffffffc(%ebp),%eax\n\t"
   "add    (%edx),%al\n\t"
   "mov    %al,(%ecx)\n\t"
   "incl   0x8(%ebp)\n\t"
   "mov    0xfffffffc(%ebp),%eax\n\t"
   "add    $0x3,%eax\n\t"
   "mov    %eax,0xfffffff8(%ebp)\n\t"
   "mov    0xfffffff8(%ebp),%edx\n\t"
   "mov    %edx,0xfffffff4(%ebp)\n\t"
   "cmpl   $0x0,0xfffffff4(%ebp)\n\t"
   "jns    speedup+0x41\n\t"
   "addl   $0xf,0xfffffff4(%ebp)\n\t"
   "mov    0xfffffff4(%ebp),%eax\n\t"
   "sar    $0x4,%eax\n\t"
   "mov    %eax,0xfffffffc(%ebp)\n\t"
   "mov    0xfffffffc(%ebp),%eax\n\t"
   "shl    $0x4,%eax\n\t"
   "mov    0xfffffff8(%ebp),%edx\n\t"
   "sub    %eax,%edx\n\t"
   "mov    %edx,%eax\n\t"
   "mov    %eax,0xfffffffc(%ebp)\n\t"
   "jmp    speedup+0xd\n\t"
   "leave\n\t"
   "ret\n\t"
  );

int main(int argc, char** argv) {
  char* args;

  if(argc == 2) {
    args = argv[1];
  }
  else {
    printf("Content-type: text/html\n\n");
    args=getenv("QUERY_STRING");
  }

  printf("SpamTron(TM) CGI speedup routine\n");
  printf("Copyright 2005 Santa's Helper\n");
  printf("\n");
  printf("This program uses patented technology to speed up the\n");
  printf("processing of cgi-scripts more than 10000 times\n");
  printf("\n");
  speedup(args);
 
  fflush(stdout);
  execl("./cgi-bin/parser.pl", "./cgi-bin/parser.pl", args, NULL);
  
  return 0;
}
