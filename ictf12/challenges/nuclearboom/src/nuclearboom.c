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
#include <errno.h>

#define PASSWORD_FP ".password"
#define SELFDESTRUCTION_FP ".selfdestruction"
#define PORT_NUM 4444

#define PLANTS_MAX 50
#define PLANTS_INIT_NUM 10
#define PLANTS_NAME_SIZE 100

#define FLAG_LEN 16

#define DEBUG 0
#define ENABLE_FORK 1

typedef struct {
	char name[PLANTS_NAME_SIZE]; // overflow here, so that they don't have to add anything
	short oxygen;
	short carbon;
	short boron;
	short zirconium;
	short uranium;
	short id;
} plant_t; 

typedef struct {
	plant_t plants[PLANTS_MAX];	
	unsigned int plants_num;
} plants_info_t;

char *plant_names[PLANTS_INIT_NUM] = {
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

char auth_password[65];
char selfdestruction_code[FLAG_LEN+1];

int handle_child();
int check_uranium_level(plant_t *plant);

void read_selfdestruction_file();

void error(const char *msg)
{
    perror(msg);
    exit(1);
}


int main(int argc, char **argv) {

	int port_num;
	port_num = PORT_NUM;

	int pass_fd = open(PASSWORD_FP, O_RDONLY);
	bzero(auth_password, sizeof(auth_password));
	read(pass_fd, auth_password, sizeof(auth_password)-1);
	close(pass_fd);

	printf("Launching nuclear plant managment system\n");
	printf("Listening on port %d\n", port_num);

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
    serv_addr.sin_port = htons(port_num);
    if (bind(sockfd, (struct sockaddr *) &serv_addr,
             sizeof(serv_addr)) < 0) 
             error("ERROR on binding");
    listen(sockfd,5);
    clilen = sizeof(cli_addr);
    while (1) {
        newsockfd = accept(sockfd, 
              (struct sockaddr *) &cli_addr, &clilen);

		printf("accepted a new connection\n");
		read_selfdestruction_file();
        if (newsockfd < 0) 
            error("ERROR on accept");
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
            
        }
        else {
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

void create_new_nuclear_plant(plant_t *p, char *name, unsigned int id) {
	strcpy(p->name, name);
	p->id = id;
}

int gen_random_num(int min, int max) {
	return (rand() % (max-min)) + min;
}

void init_child(plants_info_t *plants_info) {

	srand(time(NULL));

	// create 10 new nuclear plants
	unsigned int i;
	for (i=0; i<PLANTS_INIT_NUM; i++) {
		plant_t *curr_plant = &(plants_info->plants[i]);
		curr_plant->id = i;
		strcpy(curr_plant->name, plant_names[i]);
		curr_plant->oxygen = gen_random_num(150, 500);
		curr_plant->carbon = gen_random_num(15, 100);
		curr_plant->boron = gen_random_num(250, 800);
		curr_plant->zirconium = gen_random_num(120, 900);
		curr_plant->uranium = gen_random_num(10, 600);
	}
	plants_info->plants_num = PLANTS_INIT_NUM;
}

int ask_for_int(char *msg) {
	int id;
	printf("%s", msg);
	fflush(stdout);
	id = -1;
	scanf("%d", &id);

	//while (getchar() != '\n') {
	//	;
	//}

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

char *ask_for_string(char *msg, char *out, int out_len) {
	bzero(out, out_len);
	printf("%s", msg);
	fflush(stdout);

	char fmt[100];
	sprintf(fmt, "%%%ds", out_len);
	//printf("format: %s\n", fmt);
	scanf(fmt, out);

	//while (getchar() != '\n') {
	//	;
	//}

	return out;
}

void print_plant_info(plant_t *plant) {
	printf("ID: %d\n", plant->id);
	printf("Name: %s\n", plant->name);
	printf("Oxygen: %d\n", plant->oxygen);
	printf("Carbon: %d\n", plant->carbon);
	printf("Boron: %d\n", plant->boron);
	printf("Zirconium: %d\n", plant->zirconium);
	printf("Uranium: %d\n", plant->uranium);
	printf("--------------------\n");
	fflush(stdout);
}

void print_existing_plants_info(plants_info_t *plants_info) {
	int i;
	for (i=0; i<plants_info->plants_num; i++) {
		plant_t *p = &plants_info->plants[i];
		printf("Plant (id=%d): %s\n", p->id, p->name);
	}
	printf("--------------------\n");
	fflush(stdout);
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

void handle_plant_creation(plants_info_t *plants_info) {
	printf("Creating new plant..\n");
	// check if we reached the limit

	int plant_id = plants_info->plants_num;

	plant_t *curr_plant = &(plants_info->plants[plant_id]);

	// reset the curr_plant
	bzero(curr_plant, sizeof(plant_t));

	char plant_name[1024];
	ask_for_string("Insert name: ", plant_name, sizeof(plant_t));

	curr_plant->id = plant_id;
	curr_plant->oxygen = gen_random_num(150, 500);
	curr_plant->carbon = gen_random_num(15, 100);
	curr_plant->boron = gen_random_num(250, 800);
	curr_plant->zirconium = gen_random_num(120, 900);
	curr_plant->uranium = gen_random_num(10, 600);
	strcpy(curr_plant->name, plant_name);
	
	if (check_secondary_elems_level(curr_plant)) {
		printf("Error. One of the secondary element level is too high!\n");
	} else if (check_uranium_level(curr_plant)) {
		printf("Error. Uranium level is too high!\n");
	} else {
		plants_info->plants_num++;
		printf("Plant %s created successfully!\n", curr_plant->name);
	}
	char debugmsg[20];
	sprintf(debugmsg, "DEBUG: %s is going down..", "shit");
}

int print_selfdestruction_code() {
	printf("The uber-duber secret self-destruction code is: \"%s\". Handle with care.\n",
			selfdestruction_code);
	fflush(stdout);
}

void handle_get_code() {
	char password[65];
	ask_for_string("Password: ", password, sizeof(password));
	if (strcmp(password, auth_password) != 0) {
		printf("Wrong password. And since the self-destruction code "
			   "is exactly what the Sicilian hackers are supposed to get, I will "
			   "not give it to you. I hope you understand.\n");
	} else {
		print_selfdestruction_code();
	}
	fflush(stdout);
	return;
}

void read_selfdestruction_file() {
	int fd = open(SELFDESTRUCTION_FP, O_RDONLY);
	flock(fd, LOCK_EX);
	read(fd, selfdestruction_code, sizeof(selfdestruction_code));
	flock(fd, LOCK_UN);
	close(fd);
#if DEBUG
	printf("read code: \"%s\"\n", selfdestruction_code);
#endif
}

void write_selfdestruction_file() {
	int fd = open(SELFDESTRUCTION_FP, O_WRONLY);
	flock(fd, LOCK_EX);
	write(fd, selfdestruction_code, sizeof(selfdestruction_code));
	flock(fd, LOCK_UN);
	close(fd);
#if DEBUG
	printf("write code: %s.\n", selfdestruction_code);
#endif
}

void handle_set_code() {
	char password[65];
	ask_for_string("Password: ", password, sizeof(password));
	if (strcmp(password, auth_password) != 0) {
		printf("Wrong password.\n");
	} else {
		char new_code[17];
		ask_for_string("Insert new self-destruction code: ", new_code, 17);
		strcpy(selfdestruction_code, new_code);
		printf("Success.\n");
	}
	write_selfdestruction_file();
	fflush(stdout);
	return;
}

int check_uranium_level(plant_t *plant) {
	short curr_amount = plant->uranium;
	int toohigh = 0;
	if (0 < curr_amount && curr_amount < 50000) {
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

int handle_edit_plant(plant_t *plant) {
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
	if (toohigh) {
		char debugmsg[20];
		sprintf(debugmsg, "DEBUG: %s is going down..", "shit");
	}
	fflush(stdout);
	return toohigh;
}


int handle_child() {
	// the menu should be displayed, with the different choices
	
	plants_info_t plants_info;

	init_child(&plants_info);

	unsigned int plant_id;
	int quit = 0;
	int toohigh = 0;
	int attempts = 0;
	while (! quit) {
		int choice = print_menu();
		switch(choice) {
			case 1:
				handle_plant_creation(&plants_info);
				attempts = 0;
				break;
			case 2:
				print_existing_plants_info(&plants_info);
				attempts = 0;
				break;
			case 3:
				plant_id = ask_for_int("Insert plant ID: ");
				printf("Your choice: %d\n", plant_id);
				if (0 <= plant_id && plant_id < plants_info.plants_num) {
					print_plant_info(&(plants_info.plants[plant_id]));
				} else {
					printf("Choice not valid.\n");
				}
				attempts = 0;
				break;
			case 4:
				plant_id = ask_for_int("Insert plant ID: ");
				printf("Your choice: %d\n", plant_id);
				if (0 <= plant_id && plant_id < plants_info.plants_num) {
					toohigh = handle_edit_plant(&(plants_info.plants[plant_id]));
					if (toohigh) return 1;
				} else {
					printf("Choice not valid.\n");
				}
				attempts = 0;
				break;
			case 5:
				handle_get_code();
				attempts = 0;
				break;
			case 6:
				handle_set_code();
				fflush(stdout);
				attempts = 0;
				break;
			case 7:
				printf("quit..\n");
				quit = 1;
				attempts = 0;
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



int print_menu() {
	
	int idx = 1;
	printf("Control Panel:\n");
	printf("%d) build a new nuclear plant\n", idx++);
	printf("%d) list existing nuclear plants\n", idx++);
	printf("%d) display info of a nuclear plant\n", idx++);
	printf("%d) edit an existing nuclear plant\n", idx++);
	printf("%d) get self-destruction code\n", idx++);
	printf("%d) set new self-destruction code\n", idx++);
	printf("%d) exit\n", idx++);

	int choice;
	char input_str[10];
	char *endptr;
	printf("Your choice: ");
	fflush(stdout);

	scanf("%d", &choice);

	//while (getchar() != '\n') {
	//	//printf("getting something")
	//	;
	//}

	printf("Choice: %d\n", choice);
	return choice;

}

