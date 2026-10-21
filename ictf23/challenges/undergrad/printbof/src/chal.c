#include <stdio.h>

int win(){
    system("/bin/sh");
}

int vuln(){
    setvbuf(stdout, NULL, _IOLBF,0);
    char a[100];
    fgets(a,109,stdin);
    printf(a);
    return 0;
}


int main(){
    vuln();
    return 0;
}
