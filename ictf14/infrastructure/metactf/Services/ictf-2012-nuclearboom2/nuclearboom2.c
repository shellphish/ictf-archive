// Author: Yanick

#include<stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/file.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <dirent.h>
#include <errno.h>

#define PORT_NUM 4444

#define MIN_PLANTS_NUM 10
#define MAX_PLANTS_NUM 2500
#define MAX_FILE_NUM 1000

#define PLANT_NAME_SIZE 100
#define PASSWORD_SIZE 32
#define CODE_SIZE 17
#define FILENAME_SIZE 64

// TODO disable the DEBUG
#define DEBUG 0
#define ENABLE_FORK 1

typedef struct {
    char password[PASSWORD_SIZE];
    char name[PLANT_NAME_SIZE];
    short oxygen;
    short carbon;
    short boron;
    short zirconium;
    short uranium;
    char selfdestruction_code[CODE_SIZE];
} plant_t;

typedef struct {
    plant_t plants[MAX_PLANTS_NUM];
    unsigned int plants_num;
} plants_info_t;

char *plant_names[MIN_PLANTS_NUM] = {
    "Planet X",
    "Goofy Goo",
    "Something dirty",
    "Buffalo",
    "Uranium Store",
    "MITM got nuclear",
    "LMGTFY",
    "Absofuckinglutely",
    "Yomama",
    "fulmicotone"
};

// the secret code/flag will be loaded here, so that it's easier for the teams
// to leak it.
char cached_selfdestruction_code[CODE_SIZE];


int handle_child();
void init_plants_info(plants_info_t *plants_info);
int print_menu_and_get_choice();
int handle_create_new_plant(plants_info_t* plants_info);
int handle_list_plants(plants_info_t* plants_info);
int handle_show_plant_details(plants_info_t* plants_info);
int handle_edit_plant(plants_info_t* plants_info);
int check_uranium_level(plant_t *plant);
int handle_more_uranium(plant_t *plant, short more_amount);
int check_secondary_elems_level(plant_t *plant);
int handle_more_secondary_element(plant_t *plant, short more_amount, int elem_idx);

int handle_get_code(plants_info_t* plants_info);
int handle_set_code(plants_info_t* plants_info);

void print_plant_details(plant_t* plant);
int print_selfdestruction_code();
/*void read_selfdestruction_file(char* name, char* password);*/
/*void write_selfdestruction_file(char* name, char* password, char* new_code);*/

int is_plant_valid(plant_t* plant);

// BACK-END
int load_plant_from_file(char* filename, plant_t* plant);
int write_plant_to_file(plant_t* plant);

// UTILS
int gen_random_num(int min, int max);
void gen_random_str(int len, char* s);
int ask_for_int(char *msg);
int ask_for_int_with_range(char *msg, int min, int max);
void ask_for_string(char *msg, char *out, int out_len);
void error(const char *msg);

int count_plants_on_storage();
void delete_all_plants_on_storage();



int main(int argc, char **argv) {
    printf("Launching nuclear plant management system v2.0\n");
    printf("Listening on port %d\n", PORT_NUM);

    int sockfd, newsockfd, portno, pid;
    socklen_t clilen;
    struct sockaddr_in serv_addr, cli_addr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
       error("ERROR opening socket");

    int reuseaddr_flag = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &reuseaddr_flag, sizeof(reuseaddr_flag));

    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
#if DEBUG
    serv_addr.sin_addr.s_addr = htonl(0x7F000001);
#else
    serv_addr.sin_addr.s_addr = INADDR_ANY;
#endif
    serv_addr.sin_port = htons(PORT_NUM);
    if (bind(sockfd, (struct sockaddr *) &serv_addr,
             sizeof(serv_addr)) < 0) {
         error("ERROR on binding");
    }
    listen(sockfd, 5);
    clilen = sizeof(cli_addr);
    while (1) {
        newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);

        printf("accepted a new connection\n");
        if (newsockfd < 0) {
            error("ERROR on accept");
        }
#if ENABLE_FORK
        pid = fork();
#else
        pid = 0;
#endif
        if (pid < 0)
            error("ERROR on fork");
        if (pid == 0)  {
            // child
            dup2(newsockfd, STDIN_FILENO);
            dup2(newsockfd, STDOUT_FILENO);
            dup2(newsockfd, STDERR_FILENO);
            close(sockfd);
            close(newsockfd);
            return handle_child();
        } else {
            // father
            close(newsockfd);
            // free some dead childs
            int child_status;
            waitpid(-1, &child_status, WNOHANG);
        }
    } /* end of while */
    close(sockfd);
    return 0; /* we never get here */
}


int handle_child() {
    // the menu should be displayed, with the different choices

    plants_info_t plants_info;

    init_plants_info(&plants_info);

    unsigned int plant_id;
    int quit = 0;
    int toohigh = 0;
    int attempts = 0;
    while (! quit) {
        int choice = print_menu_and_get_choice();
        switch(choice) {
            case 1:
                quit = handle_create_new_plant(&plants_info);
                break;
            case 2:
                quit = handle_list_plants(&plants_info);
                break;
            case 3:
                quit = handle_show_plant_details(&plants_info);
                break;
            case 4:
                quit = handle_edit_plant(&plants_info);
                break;
            case 5: {
                quit = handle_get_code(&plants_info);
                break;
            }
            case 6: {
                quit = handle_set_code(&plants_info);
                break;
            }
            case 7:
                printf("quit..\n");
                quit = 1;
                break;
            default:
                printf("Choice not valid.\n");
                attempts++;
                if (attempts > 3) {
                    printf("Too many attempts..\n");
                    exit(1);
                }
                break;
        }
        fflush(stdout);
    }
    fflush(stdout);
    return 0;
}


void init_plants_info(plants_info_t *plants_info) {
    // TODO read plants from file system
    // TODO after loading it, check it.
    // TODO when found invalid one, discard it.

    srand(time(NULL));

    if (count_plants_on_storage() > MAX_FILE_NUM) {
        delete_all_plants_on_storage();
    }

    plants_info->plants_num = 0;

    unsigned int i;
    for (i=0; i<MIN_PLANTS_NUM; i++) {
        plant_t *curr_plant = &(plants_info->plants[i]);
        gen_random_str(gen_random_num(10,25), curr_plant->name);
        curr_plant->oxygen = gen_random_num(150, 500);
        curr_plant->carbon = gen_random_num(15, 100);
        curr_plant->boron = gen_random_num(250, 800);
        curr_plant->zirconium = gen_random_num(120, 900);
        curr_plant->uranium = gen_random_num(10, 600);
        plants_info->plants_num += 1;
    }

    // load plants from files

    // list all file names, and for each compatible one, load it.

    char curr_filename[FILENAME_SIZE];
    DIR *d;
    struct dirent *dir;
    d = opendir(".");
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            strcpy(curr_filename, dir->d_name);
            // check if it has the "id.plant" format
            char *dot = strrchr(curr_filename, '.');
            if (dot && !strcmp(dot, ".plant")) {
                int curr_plant_id = plants_info->plants_num++;
                load_plant_from_file(curr_filename, &(plants_info->plants[curr_plant_id]));
                /*printf("FOUND plant: %s ~> %d\n", curr_filename, curr_plant_id);*/
            }
        }
        closedir(d);
    }
}


int count_plants_on_storage() {
    char curr_filename[FILENAME_SIZE];
    DIR *d;
    struct dirent *dir;
    int count = 0;
    d = opendir(".");
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            strcpy(curr_filename, dir->d_name);
            // check if it has the "id.plant" format
            char *dot = strrchr(curr_filename, '.');
            if (dot && !strcmp(dot, ".plant")) {
                count++;
            }
        }
        closedir(d);
    }
    return count;
}


void delete_all_plants_on_storage() {
    char curr_filename[FILENAME_SIZE];
    DIR *d;
    struct dirent *dir;
    d = opendir(".");
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            strcpy(curr_filename, dir->d_name);
            // check if it has the "id.plant" format
            char *dot = strrchr(curr_filename, '.');
            if (dot && !strcmp(dot, ".plant")) {
                printf("Clearing up %s\n", curr_filename);
                unlink(curr_filename);
            }
        }
        closedir(d);
    }
}


int print_menu_and_get_choice() {
    int idx = 1;
    printf("Control Panel of NuclearBoom v2.0 (the previous version was vulnerable ;)):\n");
    printf("%d) build a new nuclear plant\n", idx++);
    printf("%d) list existing nuclear plants\n", idx++);
    printf("%d) display info of a nuclear plant\n", idx++);
    printf("%d) edit an existing nuclear plant\n", idx++);
    printf("%d) get self-destruction code for a given nuclear plant\n", idx++);
    printf("%d) set new self-destruction code for a given nuclear plant\n", idx++);
    printf("%d) exit\n", idx++);

    int choice;
    char input_str[10];
    char *endptr;
    printf("Your choice: ");
    fflush(stdout);

    scanf("%d", &choice);

    // TODO do sanity check

    printf("Choice: %d\n", choice);
    return choice;
}


int handle_create_new_plant(plants_info_t* plants_info) {
    printf("Creating new plant..\n");

    // TODO check if we reached the limit

    // get new next plant id
    int plant_id = plants_info->plants_num;

    // get a reset the current plant
    plant_t* curr_plant = &(plants_info->plants[plant_id]);
    bzero(curr_plant, sizeof(plant_t));

    char plant_name[PLANT_NAME_SIZE];
    char password[512]; // overflow
    char code[CODE_SIZE];

    ask_for_string("Insert new plant name: ", plant_name, sizeof(plant_name));

    strcpy(curr_plant->name, plant_name);
    curr_plant->oxygen = gen_random_num(150, 500);
    curr_plant->carbon = gen_random_num(15, 100);
    curr_plant->boron = gen_random_num(250, 800);
    curr_plant->zirconium = gen_random_num(120, 900);
    curr_plant->uranium = gen_random_num(10, 600);

    printf("Almost there. Now let's talk security.\n");
    ask_for_string("Insert new password: ", password, sizeof(password));
    strcpy(curr_plant->password, password);

    ask_for_string("Insert new self-destruction code: ", code, sizeof(code));
    strcpy(curr_plant->selfdestruction_code, code);

    printf("Solid! Now let's check the physical security..\n");

    if (check_secondary_elems_level(curr_plant)) {
        printf("Error. One of the secondary element level is too high!\n");
    } else if (check_uranium_level(curr_plant)) {
        printf("Uranium overflow alert! Too high!\n");
    } else {
        write_plant_to_file(curr_plant);
        printf("Everything looks good! Can you believe it? Plant \"%s\" was successfully created!\n", curr_plant->name);
        plants_info->plants_num++;
    }

    // TODO return proper quit
    return 0;
}


int handle_list_plants(plants_info_t *plants_info) {
    int i;
    for (i=0; i<plants_info->plants_num; i++) {
        plant_t *p = &plants_info->plants[i];
        printf("Plant (#%d): %s\n", i, p->name);
    }
    printf("--------------------\n");
    fflush(stdout);

    // TODO return proper quit
    return 0;
}


int handle_show_plant_details(plants_info_t* plants_info) {
    int plant_id = ask_for_int("Insert plant ID: ");
    printf("Your choice: %d\n", plant_id);
    if (! (0 <= plant_id && plant_id < plants_info->plants_num)) {
        printf("Choice not valid.\n");
        return 1;
    }

    plant_t* plant = &(plants_info->plants[plant_id]);
    print_plant_details(plant);

    fflush(stdout);

    // TODO return proper quit
    return 0;
}


void print_plant_details(plant_t* plant) {
    printf("Name: %s\n", plant->name);
    printf("Password: ********\n");
    printf("Self-destruction code: ********\n");
    printf("Oxygen: %d\n", plant->oxygen);
    printf("Carbon: %d\n", plant->carbon);
    printf("Boron: %d\n", plant->boron);
    printf("Zirconium: %d\n", plant->zirconium);
    printf("Uranium: %d\n", plant->uranium);
    printf("--------------------\n");
    fflush(stdout);
}


int handle_edit_plant(plants_info_t* plants_info) {
    int plant_id = ask_for_int("Insert plant ID: ");
    printf("Your choice: %d\n", plant_id);
    if ( ! (0 <= plant_id && plant_id < plants_info->plants_num)) {
        printf("Choice not valid.\n");
        return 1;
    }

    plant_t* plant = &(plants_info->plants[plant_id]);

    printf("What do you want to add?\n");
    printf("1) Oxygen\n");
    printf("2) Carbon\n");
    printf("3) Boron\n");
    printf("4) Zirconium\n");
    printf("5) Uranium\n");

    int more_what = ask_for_int("Choice: ");
    int more_amount = ask_for_int_with_range("How much more (0-10000): ", 0, 10000);

    int toohigh = 0;
    switch(more_what) {
        case 1: case 2: case 3: case 4:
            toohigh = handle_more_secondary_element(plant, more_amount, more_what);
            break;
        case 5:
            toohigh = handle_more_uranium(plant, more_amount);
            break;
        default:
            printf("Not valid choice.\n");
            break;
    }
    fflush(stdout);

    if (toohigh) {
        // TODO fix this
        printf("TOO HIGH!\n");
        return 1;
    }
    return 0;
}


int check_uranium_level(plant_t *plant) {
    short curr_amount = plant->uranium;
    int toohigh = 0;
    if (-2 < curr_amount && curr_amount < 50000) {
        if (curr_amount > 50000) {
            printf("Warning: uranium level really high!\n");
        } else {
            printf("OK\n");
        }
    } else {
        toohigh = 1;
        printf("ARE YOU CRAZY? Uranium in nuclear plant \"");
        printf(plant->name);
        printf("\" is TOO HIGH!\n");
    }
    return toohigh;
}


int handle_more_uranium(plant_t *plant, short more_amount) {
    int toohigh = 0;
    short int curr_amount, new_amount;

    curr_amount = plant->uranium;
    new_amount = curr_amount + more_amount;

    if (curr_amount > 22768) {
        printf("Uranium is already too much. No way you can add more.\n");
    } else {
        plant->uranium = new_amount;
        toohigh = check_uranium_level(plant);
    }
    return toohigh;
}


int check_secondary_elems_level(plant_t *plant) {
    short o, c, b, z;
    o = plant->oxygen;
    c = plant->carbon;
    b = plant->boron;
    z = plant->zirconium;

    if (!(0 < o && o < 1000)) {
        printf("Oxygen level is too high: %d (max 1000)\n", o);
    } else if (!(0 < c && c < 1000)) {
        printf("Carbon level is too high: %d (max 1000)\n", c);
    } else if (!(0 < b && b < 1000)) {
        printf("Boron level is too high: %d (max 1000)\n", b);
    } else if (!(0 < z && z < 1000)) {
        printf("Zirconium level is too high: %d (max 1000)\n", z);
    } else {
        return 0;
    }

    return 1;
}


int handle_more_secondary_element(plant_t *plant, short more_amount, int elem_idx) {
    int toohigh = 0;

    switch(elem_idx) {
        case 1:
            plant->oxygen += more_amount;
            break;
        case 2:
            plant->carbon += more_amount;
            break;
        case 3:
            plant->boron += more_amount;
            break;
        case 4:
            plant->zirconium += more_amount;
            break;
        default:
            printf("WARNING: weird elem_idx: %d\n", elem_idx);
            break;
            exit(1);
    }

    toohigh = check_secondary_elems_level(plant);
    return toohigh;
}


int handle_get_code(plants_info_t* plants_info) {
    short plant_id;
    char password[PASSWORD_SIZE];
    plant_id = ask_for_int("Insert plant ID: ");



    // TODO add sanity check
    ask_for_string("Insert plant password: ", password, sizeof(password));

    plant_t* plant = NULL;
    if (0 <= plant_id && plant_id < plants_info->plants_num) {
        plant = &(plants_info->plants[plant_id]);
    } else {
        printf("Something went wrong.\n");
        return 0;
    }

    // cache the selfdestruction_code
    strcpy(cached_selfdestruction_code, plant->selfdestruction_code);

    if (strcmp(password, plant->password) != 0) {
        printf("Nope, wrong password!! But I'm a nice guy, I'll give you the code anyways. "
               "Here it is: \"********\". -- The Troll.\n");
    } else {
        print_selfdestruction_code();
    }
    fflush(stdout);
    return 0;
}


int handle_set_code(plants_info_t* plants_info) {
    short plant_id;
    char password[PASSWORD_SIZE];

    plant_id = ask_for_int("Insert plant ID: ");
    ask_for_string("Insert plant password: ", password, sizeof(password));

    plant_t* plant = NULL;
    if (0 <= plant_id && plant_id < plants_info->plants_num) {
        plant = &(plants_info->plants[plant_id]);
    } else {
        printf("Something went wrong.\n");
        return 0;
    }

    if (strcmp(password, plant->password) != 0) {
        printf("Wrong password. DEEENIEEEEED.\n");
    } else {
        char new_code[CODE_SIZE];
        ask_for_string("Insert new self-destruction code for current plant: ", new_code, sizeof(new_code));
        strcpy(plant->selfdestruction_code, new_code);
        write_plant_to_file(plant);
        printf("Updated!.\n");
    }
    fflush(stdout);
    return 0;
}


int print_selfdestruction_code() {
    printf("The uber-duper secret self-destruction code is: \"%s\". Handle with care.\n",
            cached_selfdestruction_code);
    fflush(stdout);
}



int is_plant_valid(plant_t* plant) {
    if (strlen(plant->name) > PLANT_NAME_SIZE) {
        return 0;
    }
    if (strlen(plant->password) > PASSWORD_SIZE) {
        return 0;
    }
    if (strlen(plant->selfdestruction_code) > CODE_SIZE) {
        return 0;
    }
    // TODO check that all numbers are greater than zero.
    return 1;
}


// BACK-END

int load_plant_from_file(char* filename, plant_t* plant) {
    int fd = open(filename, O_RDONLY);
    flock(fd, LOCK_EX);
    read(fd, plant, sizeof(plant_t));
    flock(fd, LOCK_UN);
    close(fd);

    if (! is_plant_valid(plant)) {
        printf("The loaded plant with name %s is not valid.\n", plant->name);
        // not valid, reset
        bzero(plant, sizeof(plant_t));
        return 0;
    }
    /*print_plant_details(plant);*/
    /*printf("LOADED!\n");*/
    return 1;
}


int write_plant_to_file(plant_t* plant) {
    if (! is_plant_valid(plant)) {
        printf("Cannot store a non-valid plant!\n");
        return 0;
    }

    char filename[FILENAME_SIZE];
    sprintf(filename, "%s.plant", plant->name);
    int fd = open(filename, O_CREAT | O_WRONLY, 0660);
    flock(fd, LOCK_EX);
    write(fd, plant, sizeof(plant_t));
    flock(fd, LOCK_UN);
    close(fd);

    return 1;
}


// UTILS

int gen_random_num(int min, int max) {
    return (rand() % (max-min)) + min;
}


void gen_random_str(int len, char* s) {
    static const char alphanum[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";

    int i;
    for (i = 0; i < len; ++i) {
        s[i] = alphanum[rand() % (sizeof(alphanum) - 1)];
    }
    s[len] = 0;
}


int ask_for_int(char *msg) {
    int id;
    printf("%s", msg);
    fflush(stdout);
    id = -1;
    scanf("%d", &id);

    return id;
}


int ask_for_int_with_range(char *msg, int min, int max) {
    int more_amount = -1;
    while (1) {
        more_amount = ask_for_int(msg);
        if (more_amount >= min && more_amount <= max) {
            break;
        } else {
            printf("The amount should be between %d and %d\n", min, max);
        }
    }
    return more_amount;
}


void ask_for_string(char *msg, char *out, int out_len) {
    bzero(out, out_len);
    printf("%s", msg);
    fflush(stdout);

    char fmt[100];
    sprintf(fmt, "%%%ds", out_len);
    //printf("format: %s\n", fmt);
    scanf(fmt, out);
}


void error(const char *msg) {
    perror(msg);
    exit(1);
}
