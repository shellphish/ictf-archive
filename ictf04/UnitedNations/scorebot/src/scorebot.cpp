#include "util.hpp"
#include "scorebotconf.hpp"
#include "lockfile.hpp"

#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <iostream>
using namespace std;

#define DEFAULT_CONFIG "/etc/scorebot.d/scorebot.conf"

static char* prgname;

void do_process(vector<Service*> services, class NetworkUsage* usage);

void usage() {
  cerr << "Usage: " << prgname << " [Flags]...\n";
  cerr << "         [-C FILENAME]  Use FILENAME as config file\n";
  cerr << "         [-i]           Init (clear) all previous state\n";
  cerr << "         [-d]           Don't dameonize\n";
  exit(1);
}

void cleanup() {
  LockFile* lock = Globals::get()->getLockfile();
  if(lock) {
    cerr << "Deleting lock\n";
    lock->destroy();
  }
  else {
    cerr << "No lock to delete\n";
  }
}

void do_daemonize() {
  int fd;
  
  switch (fork()) {
  case -1:
    cerr << "Error forking\n";
    exit(1);
  case 0:
    break;
  default:
    exit(0);
  }

  if (setsid() == -1) {
    cerr << "setsid error\n";
    exit(1);
  }

  ofstream pid(Globals::get()->getPidfile().c_str(), ofstream::trunc);
  if(pid.good()) {
    pid << getpid();
    pid.close();
  }
  else {
    cerr << "error opening pidfile (" << Globals::get()->getPidfile() << ")" << endl;
    exit(1);
  }
  
  if ((fd = open("/dev/null", O_RDWR, 0)) != -1) {
    dup2(fd, STDIN_FILENO);
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);
    if (fd > 2)
      close (fd);
  }
  else {
    cerr << "error opening /dev/null\n";
    exit(1);
  }
  
  
  return;
}

void sig_handler(int signal){
  string sig_name = "";
  if (signal == SIGTERM) sig_name = "SIGTERM";
  else if (signal == SIGHUP) sig_name = "SIGHUP";
  else if (signal == SIGINT) sig_name = "SIGINT";
  else if (signal == SIGALRM) {
    // For timeouts, ignore
    LOG("Got alrm\n");
    return;
  }
  else {
    LOG("Caught unknown signal, terminating");
    Globals::get()->setTerminate();
    return;
  }

  LOG("Caught signal " << sig_name << ", terminating");
  Globals::get()->setTerminate();
  if(signal == SIGTERM) {
    cleanup();
    exit(0);
  }
} 



int main(int argc, char** argv) {
  prgname = argv[0];
  string configfile = DEFAULT_CONFIG;
  bool init = false;
  bool daemonize = true;
  int carg = 1;
  
  while (carg < argc) {
    if(string(argv[carg]) == "-C") {
      if(++carg == argc) usage();
      configfile = argv[carg];
    }
    else if(string(argv[carg]) == "-i") {
      init = true;
    }
    else if(string(argv[carg]) == "-d") {
      daemonize = false;
    }
    else {
      usage();
    }
    carg++;
  }

  if(carg != argc) usage();
  
  // Seed doesn't really matter
  srand(1909020002LU);
  
 cerr << "Configfile: " << configfile << endl;
 ConfigFile conf(configfile);
 if(!conf.parse(init)) {
   cleanup();
   return 1;
 }

 if(init) {
   cerr << "Statefiles initialized\n";
   cleanup();
   return 0;
 }

 // Check logfile
 if(!Globals::get()->getLog()->good()) {
   cerr << "Could not open logfile, exiting" << endl;
   cleanup();
   return 1;
 }
 
 if(!conf.restoreState()) {
   cerr << "Could not restore old state" << endl;
   cleanup();
   return 1;
 }

 // These guys restarts most syscalls if they are interrupted. This is OK.
 signal(SIGTERM, sig_handler);
 signal(SIGHUP, sig_handler);
 signal(SIGINT, sig_handler);
 

 chdir(Globals::get()->getScriptdir().c_str());

 if(daemonize) {
   cerr << "Everything looks OK, daemonizing\n";
   do_daemonize();
   
 }

 LOG("Scorebot starting");
 do_process(conf.getServices(), conf.getNetworkUsage());
 LOG("Scorebot terminated");
 
 cleanup();
 return 0;
}
