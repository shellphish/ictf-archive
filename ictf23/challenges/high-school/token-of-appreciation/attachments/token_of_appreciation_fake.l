/* Flex Scanner:
 * Description: This is a simple scanner that will read in the flag and replace it with "Correct!". Anything else will be replaced with "Incorrect!".
 */

%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
%}

%%
fake_fake_oh_this_is_so_fake {printf("Correct!\n");}
.* {printf("Incorrect!\n");}

%%

int main() {
    yylex();
}