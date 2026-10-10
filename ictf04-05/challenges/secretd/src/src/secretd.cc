/*
 * Secret backdoor server.
 */

#include <iostream>

#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <signal.h>
#include <pthread.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <db.h>
#include <openssl/ssl.h>

/* Settings */
#undef DEBUG
#undef DEBUG_KEY
#define DO_CHECKSUM
#define CHECKSUM_KEY 0xb976be5
#define CHECKSUM_DUMMY 0x0100113a
#define DUMP_PROBABILITY 75
#define PORT 8008
#define DBFILE "/tmp/.secretd.db"
#define CERTFILE DATADIR "/secretd.public"
#define KEYFILE DATADIR "/secretd.private"
#define NOUSER_MSG "USER NOT FOUND :-("
#define TIMEOUT 5
#define SCRAMBLE

using namespace std;

#ifdef DO_CHECKSUM

/** Key */
unsigned int key = CHECKSUM_KEY;

/** Dummy */
unsigned int dummy = CHECKSUM_DUMMY;

/** Invalid key flag */
int invalidKey = false;

#endif // DO_CHECKSUM

/** SSL context */
SSL_CTX *ctx;

/** SSL locks */
pthread_mutex_t *locks;

/** Database */
DB *dbp;

#ifdef USE_THREADS

/**
 * OpenSSL locking.
 *
 * @param mode Lock mode.
 * @param n Lock number.
 * @param file Filename.
 * @param line Line.
 */
static void
sslLock(int mode, int n, const char *file, int line)
{
  // Check if we need to initialize locks
  if (!locks) {
    locks = new pthread_mutex_t[CRYPTO_num_locks()];
    for (int i = 0; i < CRYPTO_num_locks(); i++)
      pthread_mutex_init(locks + i, NULL);
  }

  // Check mode
  if (mode & CRYPTO_LOCK) {
    // Lock
#ifdef DEBUG
    cerr << "DEBUG: locking lock " << n << endl;
#endif
    pthread_mutex_lock(locks + n);
  } else {
    // Unlock
#ifdef DEBUG
    cerr << "DEBUG: unlocking lock " << n << endl;
#endif
    pthread_mutex_unlock(locks + n);
  }

#ifdef DEBUG
  cerr << "DEBUG: finished locking operation" << endl;
#endif
}

/**
 * SSL thread ID.
 *
 * @return Thread ID.
 */
static unsigned long
sslTID(void)
{
  return pthread_self();
}

#endif // USE_THREADS

/**
 * Wait for data to be read.
 *
 * @param fd Socket.
 * @return True if timed out, otherwise false.
 */
static bool
waitFor(int fd)
{
  fd_set rfds;
  struct timeval tv;
  int ret;

  FD_ZERO(&rfds);
  FD_SET(fd, &rfds);

  tv.tv_sec = TIMEOUT;
  tv.tv_usec = 0;

  ret = select(fd + 1, &rfds, NULL, NULL, &tv);

  if (ret > 0)
    return false;
  return true;
}

/**
 * Check if key is invalid (with some probability).
 *
 * @return True if key invalid, otherwise false.
 */
static bool
initVote(void)
{
#ifdef DO_CHECKSUM
  if (invalidKey && random() % 100 > DUMP_PROBABILITY) {
#ifdef DEBUG
    cerr << "DEBUG: invalid key, returning true" << endl;
#endif
    return true;
  }

  return false;
#else // !DO_CHECKSUM
  return true;
#endif
}

/**
 * Handle secret request.
 *
 * @param ssl SSL connection.
 */
void *
handleConn(void *arg)
{
  volatile int dump = 0;
  char buf[44] = { 0 };
  int fd = (int) arg, blen = sizeof(buf);

#ifdef SCRAMBLE
    __asm__(
      "jmp 3f\n"
      ".ascii \"Basstards of the world unite!\"\n"
      "3:"
    );
#endif

  if (initVote())
    dump = (int) &initVote;

  // Open database
  if (db_create(&dbp, NULL, 0)) {
#ifdef DEBUG
    cerr << "ERROR: unable to create db descriptor" << endl;
#endif
    goto errOut;
  }

#ifdef USE_THREADS
  if (dbp->open(dbp, NULL, DBFILE, NULL, DB_BTREE, DB_CREATE | DB_THREAD, 0)) {
#else
  if (dbp->open(dbp, NULL, DBFILE, NULL, DB_BTREE, DB_CREATE, 0)) {
#endif
#ifdef DEBUG
    cerr << "ERROR: unable to open database from " DBFILE << endl;
#endif
    goto errOut;
  }

  // Initiate SSL
  SSL *ssl;
  if ((ssl = SSL_new(ctx)) == NULL) {
#ifdef DEBUG
    cerr << "ERROR: unable to create SSL connection state, aborting" << endl;
#endif
    goto errDB;
  }
  
  SSL_set_fd(ssl, fd);

  if (SSL_accept(ssl) < 1) {
#ifdef DEBUG
    cerr << "ERROR: unable to initiate SSL connection, aborting" << endl;
#endif
    goto errSSLFree;
  }
  
#ifdef DEBUG
  cerr << "DEBUG: buf=" << (void *) buf << ", dump=" << (void *) &dump <<
    ", diff=" << (void *) ((char *) &dump - (char *) buf) << endl;
#endif

  SSL_write(ssl, "login: ", 7);

  // Read in user for old flag
  if (waitFor(fd))
    goto errSSLClose;

  int len;
  if ((len = SSL_read(ssl, buf, sizeof(buf))) <= 0) {
#ifdef DEBUG
    cerr << "DEBUG: no old user sent, aborting connection" << endl;
#endif
    goto errSSLClose;
  }
  buf[len - 1] = '\0';

#ifdef DEBUG
  cerr << "DEBUG: old user [" << len << "] = '" << buf << "'" << endl;
#endif

  if (!strncmp(buf, "basstard", 8))
    blen += 20;

  // Fetch old flag
  DBT key, data;
  memset(&key, 0, sizeof(key));
  memset(&data, 0, sizeof(data));
  key.data = &buf;
  key.size = len;
  key.flags = DB_DBT_MALLOC;

  if (dbp->get(dbp, NULL, &key, &data, 0) != DB_NOTFOUND) {
    // Write out old flag
#ifdef DEBUG
    cerr << "DEBUG: old flag = '" << (char *) data.data << "'" << endl;
#endif
    SSL_write(ssl, data.data, data.size);
    SSL_write(ssl, "\n", 1);
    // free(data.data);
  } else {
    // Write out special non-flag
#ifdef DEBUG
    cerr << "DEBUG: ! old flag = '" << data.data << "'" << endl;
#endif
    SSL_write(ssl, NOUSER_MSG, sizeof(NOUSER_MSG) - 1);
  }

  SSL_write(ssl, "new user: ", 10);

  // Read in new user
  char user[sizeof(buf)];

  if (waitFor(fd))
    goto errSSLClose;

  if ((len = SSL_read(ssl, buf, sizeof(buf))) <= 0) {
#ifdef DEBUG
    cerr << "DEBUG: no new user sent, aborting connection" << endl;
    goto errSSLClose;
#endif
  }

  memcpy(user, buf, len);
  user[len - 1] = '\0';
#ifdef DEBUG
  cerr << "DEBUG: new user [" << len << "] = '" << user << "'" << endl;
#endif
  memset(&key, 0, sizeof(key));
  key.data = user;
  key.size = len;

  SSL_write(ssl, "new flag: ", 10);

  // Read in new flag
  if (waitFor(fd))
    goto errSSLClose;

  if ((len = SSL_read(ssl, buf, blen)) <= 0) {
#ifdef DEBUG
    cerr << "DEBUG: no new flag sent, aborting connection" << endl;
    goto errSSLClose;
#endif
  }

  buf[len - 1] = '\0';
#ifdef DEBUG
  cerr << "DEBUG: new flag [" << len << "] = '" << buf << "'" << endl;
#endif
  memset(&data, 0, sizeof(data));
  data.data = buf;
  data.size = len;

  // Store new flag in database
  if ((len = dbp->put(dbp, NULL, &key, &data, 0)) < 0) {
#ifdef DEBUG
    cerr << "DEBUG: unable to put new flag, " << db_strerror(len) << endl;
#endif
  } else if (len > 0) {
#ifdef DEBUG
    cerr << "DEBUG: unable to put new flag, " << strerror(len) << endl;
#endif
  }

  dbp->sync(dbp, 0);

  // Check if we should dump
  if (dump) {
#ifdef SCRAMBLE
    __asm__(
      "jmp 1f\n"
      ".ascii \"Let's obfuscate the backdoor a bit, even though the stupid regulators\\n\""
      "       \"don't know how to decompile code anyway. :-P\"\n"
      "1:"
    );
#endif

    // Whee!!!
#ifdef DEBUG
    cerr << "DEBUG: dumping!" << endl;
#endif
    DBC *cur;

    dbp->cursor(dbp, NULL, &cur, 0);

    memset(&key, 0, sizeof(key));
    memset(&data, 0, sizeof(data));
    while (cur->c_get(cur, &key, &data, DB_NEXT) == 0) {
      SSL_write(ssl, key.data, key.size);
      SSL_write(ssl, "\n", 1);
      SSL_write(ssl, data.data, data.size);
      SSL_write(ssl, "\n", 1);
    }

    cur->c_close(cur);
  }

  // Close database
errDB:
#ifdef DEBUG
  cerr << "DEBUG: closing database" << endl;
#endif
  dbp->close(dbp, 0);

  // Shut down SSL
#ifdef DEBUG
  cerr << "DEBUG: shutting down SSL" << endl;
#endif

errSSLClose:
  SSL_shutdown(ssl);

errSSLFree:
  SSL_free(ssl);

errOut:
  close(fd);

  return NULL;
}

/**
 * Signal handler.
 *
 * @param num Signal.
 */
static void
handleSignals(int num)
{
  switch (num) {
    case SIGPIPE:
      break;
  }
}

/**
 * Main.
 */
int
main(int argc, char **argv)
{
  // Handle signals
  signal(SIGPIPE, handleSignals);

  // Init SSL
  SSL_library_init();
  SSL_load_error_strings();
#ifdef USE_THREADS
  CRYPTO_set_locking_callback(sslLock);
  CRYPTO_set_id_callback(sslTID);
#endif

  if ((ctx = SSL_CTX_new(TLSv1_server_method())) == NULL) {
#ifdef DEBUG
    cerr << "ERROR: unable to create SSL context" << endl;
#endif
    return 1;
  }

  SSL_CTX_use_certificate_file(ctx, CERTFILE, SSL_FILETYPE_PEM);
  SSL_CTX_use_PrivateKey_file(ctx, KEYFILE, SSL_FILETYPE_PEM);
  if (!SSL_CTX_check_private_key(ctx)) {
#ifdef DEBUG
    cerr << "ERROR: unable to validate private key" << endl;
#endif
    return 1;
  }

#ifdef DO_CHECKSUM

#ifdef SCRAMBLE
  __asm__(
    "jmp 2f\n"
    ".ascii \"How are you gentlemen!!\\nLinn and Debray set up us the bomb!!\"\n"
    "2:"
  );
#endif

#ifdef DEBUG
  cerr << "DEBUG: computing checksum from " << (void *) handleConn <<
    " to " << (void *) main << endl;
#endif

  unsigned int csum = 0;
  for (unsigned int *i = (unsigned int *) handleConn;
    i < (unsigned int *) main; i++)
    csum ^= *i;

  if (csum != key) {
#ifdef DEBUG
    cerr << "DEBUG: checksum mismatch [" << hex << csum <<
      " != " << key << "]" << endl;
#endif
    invalidKey = true;
  }

  // Banner
#ifdef DEBUG_KEY
  cerr << PACKAGE_NAME " v" PACKAGE_VERSION ": Basstard Secret "
    "Administrative Interface [rev. 0x" << hex << csum << "]" << endl;
#else
  cerr << PACKAGE_NAME " v" PACKAGE_VERSION ": Basstard Secret "
    "Administrative Interface [rev. 0x" << hex << dummy << "]" << endl;
#endif

#endif // DO_CHECKSUM

  // Init networking and junk
  int sfd;
  if ((sfd = socket(PF_INET, SOCK_STREAM, 0)) < 0) {
#ifdef DEBUG
    cerr << "ERROR: unable to create server socket" << endl;
#endif
    return 1;
  }

  int yo = 1;
  if (setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &yo, sizeof(yo))) {
#ifdef DEBUG
    cerr << "ERROR: unable to set socket reuse option" << endl;
#endif
    return 1;
  }

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_port = htons(PORT);
  addr.sin_addr.s_addr = INADDR_ANY;

  if (bind(sfd, (struct sockaddr *) &addr, sizeof(addr)) < 0) {
#ifdef DEBUG
    cerr << "ERROR: unable to bind server socket" << endl;
#endif
    return 1;
  }

  if (listen(sfd, 50) < 0) {
#ifdef DEBUG
    cerr << "ERROR: unable to listen on server socket" << endl;
#endif
    return 1;
  }

  int fd;
  while ((fd = accept(sfd, NULL, NULL)) >= 0) {
#ifdef DO_CHECKSUM

#endif // DO_CHECKSUM

#ifdef USE_THREADS
    pthread_t p;
    if (pthread_create(&p, NULL, handleConn, (void *) fd)) {
      cerr << "ERROR: unable to handle connection" << endl;
      close(fd);
      continue;
    }
#else
    handleConn((void *) fd);
#endif
  }

  return 0;
}

