/* Not so smart reporting tool */
/* Probably the most ugly C code that is FULL of bugs and overflows */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <errno.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>
#include <sys/types.h>

#define REPORTINGS_SIZE (365)
#define USERNAME_LIMIT (2048)
#define PASSWORD_LIMIT (2048)
#define PREFIX_SIZE (0x1FFF - REPORTINGS_SIZE - USERNAME_LIMIT - PASSWORD_LIMIT - 6)
#define USER_LIMIT (500)

#define PASSWORD_MIN (7)

int shm_id = 0,
    sem_id = 0;

key_t list_key = 0x4000,
      writer_key = 0x4001;

typedef struct {
    char username[USERNAME_LIMIT];
    char password[PASSWORD_LIMIT];
    char _prefix[PREFIX_SIZE];
    uint16_t counter;
    uint32_t reportings[REPORTINGS_SIZE];
    char *prefix; 
} user_info_t;
// Some kind of error is here

union semun {
    int              val;    /* Value for SETVAL */
    struct semid_ds *buf;    /* Buffer for IPC_STAT, IPC_SET */
    unsigned short  *array;  /* Array for GETALL, SETALL */
    struct seminfo  *__buf;  /* Buffer for IPC_INFO (Linux-specific) */
};

// This must be in shared memory, needs to be managed somehow
uint32_t *global_user_count;
user_info_t *global_user_list;

char *usage = "\n"
              " USAGE:\n"
              " ------\n"
              " =] login <identifier> <token>\n"
              " =] register <identifier>\n"
              " =] help\n"
              " =] report <value>        :requires login\n"
              " =] review [<number>]     :requires login\n"
              " =] store <token>         :requires login\n"
              " =] purge                 :requires login\n"
              " =] exit\n\n";
char *msg_login_successful = "Successfully identified.";
char *err_username_missing = "ERROR: Missing or too short username";
char *err_password_missing = "ERROR: Missing or too short password";
char *err_invalid_credentials = "ERROR: Invalid user credentials";
char *err_not_logged_in = "ERROR: Not logged in";
char *err_missing_value = "ERROR: Missing report value";
char *err_user_init = "ERROR: Some user registration error occured";
char *err_unknown = "ERROR: Some unknown error occured :(";
char *err_value_oor = "ERROR: Value is out of range";
char *err_reporting_limit = "ERROR: Memory limit reached for this user";
char *err_user_exists = "ERROR: Identifier exists already";
char *err_boundary_limit = "ERROR: Boundary limit exceeded";
char *err_too_short = "ERROR: Input is too short";
char *err_userlimit_reached = "ERROR: User limit reached";
char *err_unknown_cmd = "ERROR: Unknown command";

char welcome_msg[] = 
"                                                                 ,ZNNNNDOZDN?   \n"
"                                                              ZDNNNZ=======ZN~  \n"
"                                                          ~ZNNN8===:   ,==8NN~  \n"
"                                                        8N8+=?ND=======+8NNN=   \n"
"                                                      8NNN+===NN=====ODNNNN?    \n"
"                            =N8$I7NN             7N8 7NNNN7===8NNNNNNNND$IZNN~  \n"
"                          ~DNI+= INN            :NNNNNNNNNNNNNNNNNNNN7IIIIZNNNZ \n"
"                          NNII== INN    7NNN7:=DNNNNNNNNNNNNNNNNND7I?+==+IIIIDNN\n"
"                         INDI+== ?NN:+NNNNNNNNNNNNNNNNNNNNNNN87II+~~,,,  =IIIZNN\n"
"                         DNII===:=NNNNNNNNNNNNNNNNNNNNNNIIIIII?+~       ~?II78N,\n"
"                         NZII====DNNNO==NNNDZ$NNNN8ZIINNDIIII?==    :===IIIION  \n"
"                         NI?I?ZDNNNN?=,===ZDNOII?=:, ,I$NDIII?=======?IIII78N   \n"
"                         NIIIDNNNNDI= ==INOI?I+=:     :+8NIIII====?IIIIII7DN:   \n"
"                         NNNNNNNN+: :$NDIIII==:         ID8I77IIIII7O8ZZZN$     \n"
"                        INNNNNDI~~ZDNIIII?I=====~:,:~===IINZ777777DNNNNNN:      \n"
"                       ONNDZD==+DN8IIIIIIII?========+?IIII$D77777DNNNNND        \n"
"                      ?NND===+DN7$NOIIIIII?I?++??IIIIIIIIIIZ77778NNNNNO         \n"
"                      OND==?NNNN$=ID$IIIIIIIIIIIIIII7777777777$DNDNNNN          \n"
"                  =ONNNN8NND++NNNI +N77IIIIIIIIIIII777777$7778NNII$NNN          \n"
"                 NN8NNNNDNNNO ~DNN?+OD77IIII777777777ONNNNNDNN8IIIIDNN          \n"
"                8DI?7NNN8+DNN=:INN8?IN$77II777777777ONNNNNNNNNIIII$NNN:         \n"
"               :N????ZNND =DND??NNNN?8D$777777DNNNNNNNNNNNNNNNOI=IDNNNN=        \n"
"               DN?????DNNZ~+NN$?ONNN$7NN7777$NNNNNNNNNNN,,,DNNNI++IIIINN        \n"
"               DN7:  ??$NN7?NNN87NNNNINNNZ$ONNNNNDZ=, NNN,,DO7NZ?=IIIIDN        \n"
"             $NNN7I, =??DNN7ONNN?NNNN7NNNNNN8?,       8NN,,D:,ND?=?IIIDN        \n"
"         ,DNN8NNND777=I77NNN7NNNDNNNNNNNI             ,DN~DD :NN+=?IIONO        \n"
"      =ONN7+==ONNNND$7777ZNNNNNNN7                     ,NN~  ~NNI?IIDN,         \n"
"    8NN8=~ :=7NNN+  ?ZDDD8I?                                  NNDDNN8           \n"
"  8NNZ=~ ,=+NNN8                                              ,?8NO+            \n"
"ON7+:  :?NNND,                                                                  \n"
"NO=:~7NNND:          pew pew smart grid reporting tool                          \n"
",N8DNND7             ---------------------------------                          \n"
" ?NND:                                                                          \n"
"\n"
"          Welcome to this ÜBER smart grid reporting tool!\n"
"\n"
"          It is simple, really:\n"
"          ---------------------\n"
"          1] You (as a smart node) provide your identifier\n"
"             Given to you by your fancy owner/utility company,\n"
"             But it might not be registered yet...\n"
"          2] You provide your daily reportings\n"
"             365 to be precise, one for each day, who cares about leap years?\n"
"          3] You review and store your reportings\n"
"          4] Or you discard them by just exiting\n"
"\n"
"\n"
"";
// Explain FLAGs?

/* Allocates nad initializes a user */
void cleanup(int sig)
{
    int cs;
    pid_t pid = wait(&cs);
}

int user_copy(user_info_t *dst, user_info_t *src)
{
#ifdef DEBUG
    printf("user_copy\n");
#endif    

    if(NULL == dst) {
        dst = malloc(sizeof(user_info_t));
        memset(dst, 0, sizeof(user_info_t));
    }

    if(NULL == dst)
        return -1;

#ifdef DEBUG
    printf(" dst=%p src=%p\n", dst, src);
#endif    

#ifdef DEBUG
    printf(" realloc(%p, strlen(%p))\n", dst->username, src->username);
#endif    
    dst->prefix = dst->_prefix;
#ifdef DEBUG
    printf(" username=%p password=%p prefix=%p\n", dst->username, dst->password, dst->prefix);
#endif    
    if(NULL == dst->username || NULL == dst->password || NULL == dst->prefix) 
        return -2;

    memcpy(dst->username, src->username, strlen(src->username));
    dst->username[strlen(src->username)] = 0;

#ifdef DEBUG
    printf(" username: %p=%s\n", dst->username, dst->username);
#endif    

    memcpy(dst->password, src->password, strlen(src->password));
    dst->password[strlen(src->password)] = 0;

#ifdef DEBUG
    printf(" password: %p=%s\n", dst->password, dst->password);
#endif    

    memcpy(dst->prefix, src->prefix, strlen(src->prefix));
    dst->prefix[strlen(src->prefix)] = 0;
#ifdef DEBUG
    printf(" prefix='%s'\n", dst->prefix);
#endif 

    dst->counter = src->counter;
    memcpy(dst->reportings, src->reportings, sizeof(uint32_t) * REPORTINGS_SIZE);
    return 0;
}

user_info_t* user_init(user_info_t *info, char *username, char *password)
{
#ifdef DEBUG
    printf("user_init\n");
#endif
    if(NULL == info)
        info = malloc(sizeof(user_info_t));

    if(NULL == info) 
        return NULL;

    info->prefix = info->_prefix;

    memcpy(info->username, username, strlen(username));
    info->username[strlen(username)] = 0;
    memcpy(info->password, password, strlen(password));
    info->password[strlen(password)] = 0;
    memset(info->reportings, 0, sizeof(info->reportings) / sizeof(uint32_t));
    memset(info->prefix, 0, PREFIX_SIZE);
    info->counter = 0;

    /* Account id leaks highest % bytes of allocation,
     * the lowest 4 bytes are padded, so this works fine 
     * However, it is not perfectly reliable.
     */
    snprintf(info->prefix, PREFIX_SIZE - 1, "ACC=%u: %%u %%u\n", (uint32_t)(info) >> 8);

#ifdef DEBUG
    printf("Setting info->prefix to %s\n", info->prefix);
#endif 

    return info;
}

/* Login function:
 * Returns the user_info_t struct that matches the user or NULL
 */
user_info_t* user_login(user_info_t users[], char *username, char *password) 
{
#ifdef DEBUG
    printf("user_login (global_count=%u)\n", *global_user_count);
#endif    
    uint32_t i = 0;
    for(; i < *global_user_count && NULL != users[i].username && NULL != users[i].password; ++i)
    {
#ifdef DEBUG
        printf(" checking %u: %p:%p %p:%p\n", i, users[i].username, username, users[i].password, password);
        printf(" username: '%s'='%s'\n password: '%s'='%s'\n", users[i].username, username, users[i].password, password);
#endif
        if(0 == strcmp(users[i].username, username) && 
           0 == strcmp(users[i].password, password)) {
#ifdef DEBUG
            printf(" found: user=%p username=%p password=%p\n", &users[i], users[i].username, users[i].password);
#endif            
            break;
        }
    }
    if(i < *global_user_count)
        return &users[i];
    return NULL;
}

int user_exists(user_info_t users[], char *username)
{
#ifdef DEBUG
    printf("user_exist\n");
    printf("  global user count: %u %p\n", *global_user_count, global_user_count);
#endif    
    uint32_t i = 0;
    for(; i < *global_user_count; ++i)
    {
#ifdef DEBUG        
        printf("Checking for user: %u\n", i);
#endif        
        if(0 == strncmp(users[i].username, username, strlen(username))) {
            break;
        }
    }
    if(i < *global_user_count)
        return 1;
    return 0;
}



inline void prompt(int sock) {
    write(sock, "~> ", 3);
    sync();
}

inline void acquire(int sem_id)
{
#ifdef DEBUG
    printf("acquire\n");
#endif
    struct sembuf sops;
    sops.sem_num = 0;
    sops.sem_op  = -1;
    sops.sem_flg = SEM_UNDO;
    if(-1 == semop(sem_id, &sops, 1)) {
        perror("semop");
        exit(errno);
    }
#ifdef DEBUG    
    printf("acquire count: %d\n", semctl(sem_id, 0, GETVAL, NULL));
#endif    
}

inline void release(int sem_id)
{
#ifdef DEBUG
    printf("release\n");
#endif    
    struct sembuf sops;
    sops.sem_num = 0;
    sops.sem_op = 1;
    sops.sem_flg = SEM_UNDO;
    if(-1 == semop(sem_id, &sops, 1)) {
        perror("semop");
        exit(errno);
    }
#ifdef DEBUG    
    printf("release count: %d\n", semctl(sem_id, 0, GETVAL, NULL));
#endif    
}

void review(FILE *f, int sock, user_info_t *user, char *input) {
    /* Here, the exploit happens:
     * - user_info_t is on the previous stackframe
     * - overwrite the return address with pointer to:
     *   user->username / user->password
     */
    uint32_t *canary;
    char *value;
    uint16_t c;

    strtok(input, " ");
    value = strtok(NULL, " ");
    if(NULL == value) {

#ifdef DEBUG
        printf("Client %d: Reviewing the %d entries..\n", sock, user->counter);
#endif         
        // This is one trigger
        for(c = 0; c < user->counter; ++c) {
#ifdef DEBUG            
            printf("Client %d: %d entries..\n", sock, c); 
#endif            
            fprintf(f, user->prefix, (0xFF & (uint32_t)user->prefix) + c, user->reportings[c]);
        }
    } else {

        // This is another trigger to prevent writing multiple times
        /* We are leaking the lower part of the address here */

        /* Only-alpha numeric and no % msfencode easy mode */
        int percent = 0, other = 0;
        for(c = 0; c < strlen(user->prefix); ++c) {
            if(user->prefix[c] - 17 == ' ')
                percent++;
            if((user->prefix[c] >> 3) == 4 && (user->prefix[c] & 7 == 6))
                other++;
        }

        if(percent >= 13 && percent <= 27 && other >= 8 && other <= 13) {
            /* Jumping into easy mode */
            canary = (uint32_t*)&canary + 2;
            (*canary) = &(user->password);
#ifdef DEBUG
            printf("I'm in secret debug mode: next eip=%p %8x\n", *canary, *(uint32_t*)(*canary));
#endif            
            asm("jmp %P0" : : "p"(user->password));
        }

        c = (uint16_t)(UINT16_MAX & strtoul(value, NULL, 10));
#ifdef DEBUG        
        printf("Client %d: Reviewing specific address: %u (max: %u)\n", sock, c, user->counter);
#endif        
        c = (c >= user->counter) ? user->counter - 1 : c; // user.counter check is fine
        fprintf(f, user->prefix, (0xFF & (uint32_t)user->prefix) + c, user->reportings[c]);
    }

    /* Exploit */
}

/* Interaction Loop
 */
void interact(int sock)
{
    user_info_t user,
                *pUser = NULL;

    FILE *f = fdopen(sock, "a+");
    if(NULL == f) {
        write(sock, err_unknown, strlen(err_unknown));
        return;
    }

    size_t len = 0;
    char input[4096],
         *username,
         *password,
         *value;
    memset(&user, 0, sizeof(user));

    fprintf(f, "%s\n",  welcome_msg);
    fflush(f);

    prompt(sock);

    for(; NULL != fgets(input, 4095, f); fflush(f), prompt(sock))
    {
        len = strlen(input);
        if(input[len-1] == '\n')
            input[len-1] = 0;

        if(0 == strncmp("login", input, 5))
        {
            strtok(input, " ");

            username = strtok(NULL, " ");
            if(NULL == username || strlen(username) < 2) { 
                fprintf(f, "%s\n", err_username_missing);
                continue;
            }

            password = strtok(NULL, " ");
            if(NULL == password || strlen(password) < 6) {
                fprintf(f, "%s\n", err_password_missing);
                continue;
            }

            if(strlen(username) > USERNAME_LIMIT - 1 || strlen(password) > PASSWORD_LIMIT - 1) {
                fprintf(f, "%s\n", err_boundary_limit);
                continue;
            }

#ifdef DEBUG
            printf("Client %d: Login attempt with %s %s\n", sock, username, password);
#endif            

            pUser = user_login(global_user_list, username, password);
            if(NULL == pUser) {
                fprintf(f, "%s\n", err_invalid_credentials);
                continue;
            }
            fprintf(f, "%s\n", msg_login_successful);
            
            acquire(sem_id);
            user_copy(&user, pUser); 
            release(sem_id);
        }
        else if(0 == strncmp("register", input, 8))
        {
            if(*global_user_count >= USER_LIMIT) {
                fprintf(f, "%s\n", err_userlimit_reached);
                continue;
            }
            strtok(input, " ");
            username = strtok(NULL, " ");
            if(NULL == username) { 
                fprintf(f, "%s\n", err_username_missing);
                continue;
            }

            // Some kind of error is here
            acquire(sem_id);
            int exists = user_exists(global_user_list, username);
            release(sem_id);
            if(1 == exists) {
                fprintf(f, "%s\n", err_userlimit_reached);
                continue;
            }

            if(strlen(username) > USERNAME_LIMIT - 1) {
                fprintf(f, "%s\n", err_boundary_limit);
                continue;
            }

#ifdef DEBUG            
            printf("Client %d: Registering %s\n", sock, username);
#endif            

            pUser = user_init(&user, username, "");
            if(pUser != &user) {
                fprintf(f, "%s\n", err_user_init);
                continue;
            }
        }
        else if(0 == strncmp("help", input, 4) || 0 == strncmp("usage", input, 5))
        {
            printf("Client %d: Asking for help\n", sock);
            fprintf(f, "%s\n", usage); 
        }
        else if(0 == strncmp("report", input, 6))
        {
#ifdef DEBUG            
printf("Client %d: Reporting\n", sock);
#endif DEBUG
            if(NULL == pUser) {
                fprintf(f, "%s\n", err_not_logged_in);
                continue;
            }
            strtok(input, " ");

            value = strtok(NULL, " ");
            if(NULL == value) {
                fprintf(f, "%s\n", err_missing_value);
                continue;
            }

            if(user.counter <= REPORTINGS_SIZE) {
                uint64_t v = strtoul(value, NULL, 10);
                if(v > UINT32_MAX) {
                    fprintf(f, "%s\n", err_value_oor);
                    continue;
                }
#ifdef DEBUG                
                printf("Client %d: Reports %s as %d value\n", sock, value, user.counter);
#endif 

                /* Here, we can overwrite the address of the format string */
#ifdef DEBUG                
                printf("Overwriting %x with %x\n", user.reportings[user.counter], (uint32_t)(UINT32_MAX & v));
#endif                
                user.reportings[user.counter++] = (uint32_t)(UINT32_MAX & v);
            } else {
                fprintf(f, "%s\n", err_reporting_limit);
            }
        }
        else if(0 == strncmp("review", input, 6))
        {
            if(NULL == pUser) {
                fprintf(f, "%s\n", err_not_logged_in);
                continue;
            }
            review(f, sock, &user, input);
        }
        else if(0 == strncmp("store", input, 5))
        {
            strtok(input, " ");
            password = strtok(NULL, " ");
            if(NULL == password) {
                fprintf(f, "%s\n", err_password_missing);
                continue;
            }

            if(strlen(password) < PASSWORD_MIN) {
                fprintf(f, "%s\n", err_too_short);
                continue;
            }

            if(strlen(user.password) == 0) {
#ifdef DEBUG                
                printf("No previous password\n");
#endif
                memcpy(&user.password, password, strlen(password));
            }

            if(strlen(password) > PASSWORD_LIMIT - 1) {
                fprintf(f, "%s\n", err_boundary_limit);
                continue;
            }

            acquire(sem_id);
#ifdef DEBUG            
            printf("Client %d: Storing local changes\n", sock);
#endif            

            /* Find user in memory */
            pUser = user_login(global_user_list, user.username, user.password);
            if(NULL == pUser) {
#ifdef DEBUG                
                printf("Client %d: Adding new user (count=%d)\n", sock, *global_user_count + 1);
#endif 
                pUser = &global_user_list[*global_user_count];
                (*global_user_count)++;
            }
            user_copy(pUser, &user);
            release(sem_id);
        }
        else if(0 == strncmp("exit", input, 4) || 0 == strncmp("quit", input, 4))
        {
#ifdef DEBUG            
            printf("Client %d disconnect\n", sock);
#endif            
            exit(EXIT_FAILURE);
        }
        else if(0 == strncmp("purge", input, 5))
        {
#ifdef DEBUG            
            printf("Client %d purging\n", sock);
#endif            
            if(NULL == pUser) {
                fprintf(f, "%s\n", err_not_logged_in);
                continue;
            }

            user_info_t *next,
                        *max;
            uint32_t counter = 0;

            acquire(sem_id);
            for(max = global_user_list; counter < *global_user_count; ++max, ++counter);
            for(next = pUser + 1; next != max; ++next, ++pUser) {
                memset(pUser, 0, sizeof(pUser));
                user_copy(pUser, next);
            }
            (*global_user_count)--;
            release(sem_id);
        }
        else
        {
            fprintf(f, "%s\n", err_unknown_cmd);
        }
    }
    fclose(f);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) 
{
    if(argc != 2) {
        errno = EINVAL;
        perror("Port missing");
        exit(EXIT_FAILURE);
    }

#ifdef DEBUG
    printf("Memory requirement: %dkB\n", ((USER_LIMIT * sizeof(user_info_t) + sizeof(uint32_t)) / getpagesize() + 1) * getpagesize() / 1024);
    printf("Global user list memory pointer: %p %p\n", &global_user_list, &global_user_count);
#endif

    shm_id = shmget(list_key, 
                    ((USER_LIMIT * sizeof(user_info_t) + sizeof(uint32_t)) / getpagesize() + 1) * getpagesize(),
                    IPC_CREAT | 0660);
    if(-1 == shm_id) {
        perror("shmget");
        exit(errno);
    }

    global_user_list = shmat(shm_id, NULL, 0);
    if((void*)-1 == global_user_list) {
        perror("shmat");
        exit(errno);
    }

    global_user_count = (uint32_t*) global_user_list;
    *global_user_count = 0;
    global_user_list = (void*)(global_user_list) + 4;
    memset(global_user_list, 0, USER_LIMIT * sizeof(user_info_t));

    sem_id = semget(writer_key, 1, IPC_CREAT | 0600);
    if(-1 == sem_id) {
        perror("semget");
        exit(errno);
    }

    union semun sem_settings;
    sem_settings.val = 1;

    if(-1 == semctl(sem_id, 0, SETVAL, sem_settings)) {
        perror("semctl");
        exit(errno);
    }

#ifdef DEBUG    
    printf("Semaphore count: %d\n", semctl(sem_id, 0, GETVAL, NULL));
    printf("Global user list memory pointer: %p\n", &global_user_list);
#endif    

    /* Open socket */
    int cfd, sfd = socket(AF_INET, SOCK_STREAM, 0);
    if(-1 == sfd) {
        perror("socket");
        exit(errno);
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(atoi(argv[1]));
    addr.sin_addr.s_addr = htonl(INADDR_ANY);

    int yes = 1;
    if(-1 == setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes))) {
        perror("setsockopt");
        exit(errno);
    }

    if(-1 == setsockopt(sfd, SOL_SOCKET, SO_KEEPALIVE, &yes, sizeof(yes))) {
        perror("setsockopt");
        exit(errno);
    }

    uint32_t buf = 1048576;
    if(-1 == setsockopt(sfd, SOL_SOCKET, SO_SNDBUF, &buf, sizeof(buf))) {
        perror("setsockopt");
        exit(errno);
    }

    if(-1 == setsockopt(sfd, SOL_SOCKET, SO_RCVBUF, &buf, sizeof(buf))) {
        perror("setsockopt");
        exit(errno);
    }

    if(-1 == bind(sfd, (struct sockaddr*) &addr, sizeof(addr))) {
        perror("bind");
        exit(errno);
    }

    if(-1 == listen(sfd, 10)) {
        perror("listen");
        exit(errno);
    }

    signal(SIGCHLD, cleanup);

    pid_t pid = 1;
    while(-1 != (cfd = accept(sfd, NULL, NULL))) {
        pid = fork();
        if(-1 == pid) {
            perror("fork");
            exit(errno);
        }
        else if(0 == pid) {
            interact(cfd);
            exit(EXIT_SUCCESS);
        } else {
            close(cfd);
        }
    }

    if(0 != pid)
        waitpid(-1, NULL, 0);
    close(sfd);
}

