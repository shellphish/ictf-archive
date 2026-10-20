#include "util.h"
#include <openssl/sha.h>
#include <string.h>


bool read_moves(thread_arg arg, char moves[MOVEMENT_LIMIT], int* n);
void joke_the_user(void);
bool parse_attack(char* str, int max, char* err_out, int);

static const char* INVALID_MOVEMENT="\nNot a valid choise!";
static const char* NEXT_MOVEMENT="\nNext move? [w,n,e,s]";
static const char* SPECIFY_MOVEMENT="\nSpecify a movement [w,n,e,s]:";
static const char* DISCOVER_MESSAGES[]={
  "Mmm.. there's nothing here.\n",
  "I cannot see anything in the woods...\n",
  "Ehi, you found OIL.\n",
  "Wow! You found gold!\n",
  "What a pretty girl here! Ops, let's focus on the target.\n",
  "AhA! You found an uranium cave!!\n",
  "Almost extremely too fast, slow down.\n",
  "Why is this place so black?!\n",
  "Some scientist is doing Uranium research here, what is it called? Urinatiion?\n", 
  "Lots of trees, and it's getting dark!\n",
  "You found Waldo!\n",
  "There's a bear.\n",
  "You found Iron!\n",
  "You found aliens, or did they find you?!\n",
  "You found a river!\n",
  "There's a candy house closeby! Is that yellow cake?\n",
  "I see some centrifuge trees!\n"
};

static const char* SQL_FAKE_ERR="There seems to be an error in your SQL query. The MySQL server error output below, if there is any, may also help you in diagnosing the problem\nERROR: Unclosed quote @ 1\nSTR: \"\nSQL: \"";

static int PROBABILITIES[]={0,40,62,66,69,71,73,74,77,78,81,82,85,90,91,96,98,100};

static void(*DISCOVER_FUNCTIONS[])(void)={
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user,
  joke_the_user
};
