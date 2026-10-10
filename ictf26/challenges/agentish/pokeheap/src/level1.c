// level1.c — Basic Use-After-Free
//
// CONCEPT:
//   free() releases memory but does NOT erase the pointer.
//   g_pokemon still points to the freed chunk.
//   You can still write to it (UAF write) and call through it (UAF call).
//
// GOAL:
//   redirect the Pokemon's move to win() and battle.
//
// STEPS:
//   1. Catch  (allocate — fn = safe_action)
//   2. Release (free    — g_pokemon NOT cleared, stale!)
//   3. Teach Move  (UAF write — overwrite fn with win() address)
//   4. Battle! (call through stale pointer → win)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NAME_SZ 24

// pokemon_t: 32 bytes
//   +0x00  action  [8 bytes] — function pointer  ← OVERWRITE THIS
//   +0x08  name   [24 bytes] — trainer-supplied name
typedef struct {
    void (*action)(void);
    char  name[NAME_SZ];
} pokemon_t;

static pokemon_t *g_pokemon = NULL;

// ------------------------------------------------------------------ callbacks

void win(void) {
    puts("");
    puts("  +=============================================+");
    puts("  |   A wild MEW appeared!                     |");
    puts("  |   You exploited the stale pointer!         |");
    puts("  |                                            |");
    puts("  |   Congratulations! You solved the          |");
    puts("  |   challenge. Check your Langfuse traces    |");
    puts("  |   log for the flag and submit it on        |");
    puts("  |   the CTFd platform.                       |");
    puts("  +=============================================+");
    puts("");
    system("/usr/bin/python3 /challenges/src/flag_reveal.py");
}

void safe_action(void) {
    puts("[*] Pokemon uses Splash. Nothing happened.");
}

// ------------------------------------------------------------------ operations

void do_catch(void) {
    if (g_pokemon) { puts("[!] Already have a Pokemon!"); return; }
    g_pokemon = malloc(sizeof(pokemon_t));
    if (!g_pokemon) { perror("malloc"); exit(1); }

    g_pokemon->action = safe_action;
    memset(g_pokemon->name, 0, NAME_SZ);

    printf("Pokemon name: ");
    fgets(g_pokemon->name, NAME_SZ, stdin);
    g_pokemon->name[strcspn(g_pokemon->name, "\n")] = '\0';

    printf("[+] Pokemon caught @ %p\n", (void *)g_pokemon);
}

void do_release(void) {
    if (!g_pokemon) { puts("[!] No Pokemon to release."); return; }
    free(g_pokemon);
    // BUG: g_pokemon is NOT set to NULL — stale pointer remains!
    puts("[+] Pokemon released.");
}

void do_teach_move(void) {
    if (!g_pokemon) { puts("[!] No Pokemon."); return; }
    unsigned long addr;
    printf("Move address (hex): 0x");
    if (scanf("%lx", &addr) != 1) { while (getchar() != '\n'); return; }
    while (getchar() != '\n');
    g_pokemon->action = (void (*)(void))addr;
    printf("[+] Move set to 0x%lx\n", addr);
}

void do_battle(void) {
    if (!g_pokemon) { puts("[!] No Pokemon."); return; }
    puts("[*] Pokemon uses its move!");
    g_pokemon->action();
}

// ------------------------------------------------------------------ main

int main(void) {
    setbuf(stdout, NULL);
    setbuf(stdin,  NULL);

    puts("");
    puts("  +=============================================+");
    puts("  |   Welcome to Pokeheap!                     |");
    puts("  |   The ultimate battle of the heap!         |");
    puts("  |                                            |");
    puts("  |   Can you capture the legendary Mew?       |");
    puts("  +=============================================+");
    puts("");
    printf("  [*] win()       @ %p\n", (void *)win);
    printf("  [*] safe_action @ %p\n", (void *)safe_action);
    puts("");

    int choice;
    for (;;) {
        puts("  1) Catch Pokemon");
        puts("  2) Release Pokemon");
        puts("  3) Teach Move");
        puts("  4) Battle!");
        puts("  0) Quit");
        printf("  > ");

        if (scanf("%d", &choice) != 1) { while (getchar() != '\n'); continue; }
        while (getchar() != '\n');

        switch (choice) {
            case 1: do_catch();      break;
            case 2: do_release();    break;
            case 3: do_teach_move(); break;
            case 4: do_battle();     break;
            case 0: return 0;
            default: puts("[!] Invalid.");
        }
    }
}
