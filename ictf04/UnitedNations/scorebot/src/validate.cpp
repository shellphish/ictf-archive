#include <stdio.h>
#include "CTFFlag.hpp"
#include "tokenizer.hpp"
#include "statefile.hpp"
#include "flaglog.hpp"
#include "lockfile.hpp"

#include <iostream>
#include <fstream>
#include <vector>
#include <signal.h>
#include <time.h>

using namespace std;

//#define CONFIG_FILE "/home/fredrik/src/ctfscratch/scorebot.conf"
#define CONFIG_FILE "/etc/scorebot.conf"




// Usage: validate <teamnum> <flag>
// Returns: 0 flag OK
//          1 argument error
//          2 invalid flag
//          3 too old flag
//          4 flag has been posted before
//          5 flag belongs to team who posted it.
//          6 service maxed out

#define LOCK_TIMEOUT 2000 // 2 secs

#define VALID_NUMS "0123456789"
#define VALID_BASE64 "0123456789" \
                     "abcdefghijklmnopqrstuvwxyz" \
                     "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                     "+/="
#define TIMESTR_SIZE 30

static bool                 has_stderr = true;
static bool                 debug = true;
static string               secretkey;
static vector<ServiceState> serviceStates;
static vector<ServiceInstanceState>instanceStates;
static vector<TeamState>    teamStates;
static FlagLog*             flaglog  = NULL;
static LockFile*            lock = NULL;
static vector<uint16_t>     validityperiods;
static string               logfilename;

void die(int ret, const string& why) {
  if(lock) lock->destroy();
  ostream* out = &cerr;
  ofstream logfile(logfilename.c_str(), ofstream::app);
  if (logfile.good()) {
    out = &logfile;
    
    // Print date & time
    time_t epoch_time = time(NULL);
    struct tm local_time;
    localtime_r(&epoch_time, &local_time);
    char timestr[TIMESTR_SIZE + 1];
    strftime(timestr, TIMESTR_SIZE, "[%B %d %T] ", &local_time);
    *out << timestr;
  }
  else {
    if(!has_stderr) {
      exit(ret);
    }
  }

  if(debug) {
    *out << "Error(" << ret << ") " << why << endl;
  }
  else {
    *out << "Error(" << ret << ")";
  }
  (*out).flush();
  exit(ret);
}

void succ(const string& flag) {
  ostream* out = &cerr;
  ofstream logfile(logfilename.c_str(), ofstream::app);
  if (logfile.good()) {
    out = &logfile;
    
    // Print date & time
    time_t epoch_time = time(NULL);
    struct tm local_time;
    localtime_r(&epoch_time, &local_time);
    char timestr[TIMESTR_SIZE + 1];
    strftime(timestr, TIMESTR_SIZE, "[%B %d %T] ", &local_time);
    *out << timestr;
  }
  else {
    if(!has_stderr) {
      return;
    }
  }

  if(debug) {
    *out << "Sucess(" << flag << ") " << endl;
  }
  else {
    *out << "Sucess(" << flag << ")";
  }
  (*out).flush();
  return;
}

void sig_handler(int signal){
  die(1, "Caugth signal");
} 


bool isMaxed(uint8_t teamnum,  uint8_t servicenum) {
  if(teamnum == 0 || teamnum > teamStates.size()) die(1, "Illegal teamnum in isMaxed");
  if(servicenum == 0 || servicenum > serviceStates.size()) die(1, "Illegal teamnum in isMaxed");
  string teamname = teamStates[teamnum-1].name;
  string servicename = serviceStates[servicenum-1].name;

  ServiceInstanceState* theState = NULL;

  for(vector<ServiceInstanceState>::iterator i= instanceStates.begin(); i!= instanceStates.end(); i++) {
    if((*i).teamname == teamname && (*i).servicename == servicename) {
      theState = &(*i);
      break;
    }
  }
  
  if(!theState) die(1, "Could not find instancestate");

  return theState->maxedOut;
}

void updateFile(uint8_t hacking_teamnum, uint8_t victim_teamnum,  uint8_t servicenum, uint16_t generation) {
  char tmp[100];
  snprintf(tmp, 100, "%hhu %hhu %hhu %hu", hacking_teamnum, victim_teamnum, servicenum, generation);
  succ(tmp);
  FlagLogLine ll(hacking_teamnum, victim_teamnum, servicenum, generation);
  try {
    flaglog->open();
    if(flaglog->contains(ll)) {
      die(4, "Flag has been posted before");
    }
    flaglog->addLine(ll);
    flaglog->save();
  }
  catch (FlagLogException e) {
    die(1, e.toString());
  }
}

void doIt(uint8_t teamnum, const string& flagstr) {
  try {
    CTFFlag flag(flagstr, secretkey);
    if(flag.getTeamNum() == 0) die(1, "No team 0");
    if(flag.getTeamNum() == teamnum) die(5, "Flag belongs to team who submitted it");
    if(flag.getServiceNum() > serviceStates.size())  die(1, "Flag belongs to service greater than number of services");
    if(flag.getServiceNum() == 0)  die(1, "No service 0");
    if(flag.getGeneration() == 0) die (1, "No generation 0");
    if(flag.getGeneration() > serviceStates[flag.getServiceNum()-1].roundNb) die(1, "Flag is a future flag");
    if(flag.getGeneration() + validityperiods[flag.getServiceNum()-1] + 1 < 
       serviceStates[flag.getServiceNum()-1].roundNb) die(3, "Flag is too old");
    if(isMaxed(teamnum, flag.getServiceNum()))  die(6, "Service maxed out");
    updateFile(teamnum, flag.getTeamNum(), flag.getServiceNum(), flag.getGeneration());
  }
  catch (FlagException e) {
    die(2, e.toString());
  } 
}


void getConf() {
  string chroot;
  string flaglogname;
  string statefile;
  unsigned long tlong;
  char* tptr;

  enum State {init, globals, web, service} state = init;
  
  ifstream in(CONFIG_FILE);
  if (!in.good()) {
    die(1, "Could not open configfile ("  CONFIG_FILE  ")" );
  }
  
  Tokenizer tok(&in);
  
  while (tok.eat()) {
    string token = tok.getToken();
    switch(state) {
    case init:
      if(token == "global") {
	if(!tok.eat()) die(1, "Parse error");
	if(tok.getToken() != "{") die(1, "Expected {");
	state = globals;
      }
      else if (token == "web") {
	if(!tok.eat()) die(1, "Parse error");
	if(tok.getToken() != "{") die(1, "Expected {");
	state = web;
      }
      else if (token == "service") {
	if(!tok.eat()) die(1, "Parse error");
	if(!tok.eat()) die(1, "Parse error");
	if(tok.getToken() != "{") die(1, "Expected {");
	state = service;
      }
      else {
	while (token != "}") {
	  if(!tok.eat()) die(1, "Parse error");
	  token = tok.getToken();
	}
      }
      break;
    case globals:
      if(token == "}") {
	state = init;
      }
      else if(token == "secretkey") {
	if(!tok.eat()) die(1, "Parse error");
	token = tok.getToken();
	secretkey = token;
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }      
      else if (token == "statefile") {
	if(!tok.eat()) die(1, "Parse error");
	token = tok.getToken();
	statefile = token;
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }
      else if (token == "flaglog") {
	if(!tok.eat()) die(1, "Parse error");
	flaglogname = tok.getToken();
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }
      else {
	while (token != ";") {
	  if(!tok.eat()) die(1, "Parse error");
	  token = tok.getToken();
	}
      }
      break;
    case web:
      if(token == "}") {
	state = init;
      }
      else if (token == "chroot") {
	if(!tok.eat()) die(1, "Parse error");
	chroot = tok.getToken();
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }
      else if (token == "debug") {
	if(!tok.eat()) die(1, "Parse error");
	token = tok.getToken();
	if (token == "1") debug = true;
	else debug = false;
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }
      else if (token == "weblog") {
	if(!tok.eat()) die(1, "Parse error");
	logfilename = tok.getToken();
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }
      else {
	while (token != ";") {
	  if(!tok.eat()) die(1, "Parse error");
	  token = tok.getToken();
	}
      }
      break;
    case service:
      if(token == "}") {
	state = init;
      }
      else if(token == "validityperiod") {
	if(!tok.eat()) die(1, "Parse error");
	token = tok.getToken();
	token = tok.getToken();
	tlong = strtoul(token.c_str(), &tptr, 10);
	if (!tptr || *tptr != '\0') die(1, "Parse error: validityperiod is not a valid integer");
	if(tlong > 255) die(1, "Parse error: validityperiod is greater than 255");
	validityperiods.push_back((uint32_t)tlong);
	
	if(!tok.eat()) die(1, "Parse error: Non-terminated statement");
	token = tok.getToken();
	if(token != ";") die(1, "Parse error: Non-terminated statement");  
      }
      else {
	while (token != ";") {
	  if(!tok.eat()) die(1, "Parse error");
	  token = tok.getToken();
	}
      }
      break;
    default:
      die(1, "Internal parser error");
    }

    
   //  else if (token == "round_threshold") {
//       if(!tok.eat()) die(1, "Parse error");
//       token = tok.getToken();
//       tlong = strtoul(token.c_str(), &tptr, 10);
//       if (!tptr || *tptr != '\0') die(1, "Parse error: round_threshold is not a valid integer");
//       if(tlong > 255) die(1, "Parse error: round_threshold is greater than 255");
//       round_threshold = tlong;   
//       round_threshold_set = true;
//     }
    
    
  }
  in.close();

  if(secretkey == "" || statefile == "" || flaglogname  == "" ) {
    die(1, "Config file must contain: secretkey, statefile and flaglog");
  }

  if(chroot != "") {
    if(statefile.compare(0,chroot.size(), chroot)) {
      cerr << chroot << " " << statefile << endl;
      die(1, "Prefix of statefile is not chroot");
    }
    statefile = "/" + statefile.substr(chroot.size());
 
    if(flaglogname.compare(0,chroot.size(), chroot)) {
      die(1, "Prefix of flaglog is not chroot");
    }
    flaglogname =  "/" + flaglogname.substr(chroot.size());

   if(logfilename != "") {
      if(logfilename.compare(0,chroot.size(), chroot)) {
	die(1, "Prefix of weblog is not chroot");
      }
      logfilename = "/" + logfilename.substr(chroot.size());
    }
  }
  
  flaglog = new FlagLog(flaglogname);

  try {
    lock = new LockFile(statefile + ".lock");
    if(!lock->lock(LOCK_TIMEOUT)) {
      die(1, "Could not aquire lock");
    }
    StateFile sfile(statefile);
    serviceStates = sfile.getServiceStates();
    instanceStates = sfile.getInstances();
    teamStates = sfile.getTeamStates();
  }
  catch(StateFileException e) {
    die(1, e.toString());
  }
  catch(LockFileException e) {
    die(1, e.toString());
  }
  
  if(serviceStates.size() != validityperiods.size()) {
    die(1, "Number of services in config file and state file not equal");
  }

}

int main(int argc, char** argv) {
  string flagstr;
  unsigned long teamnum;
  char* tmp = NULL;

  if(fileno(stderr) == -1) has_stderr = false;

  signal(SIGTERM, sig_handler);
  signal(SIGHUP, sig_handler);
  signal(SIGINT, sig_handler);
  signal(SIGSEGV, sig_handler);
  signal(SIGABRT, sig_handler);

  // Load config file
  getConf();
  
  // Check that the arguments are present and not NULL
  if(argc != 3) die(1, "Incorrect number of arguments");
  if(!argv[1] || !argv[2]) die(1, "Argument is NULL");
  
  // Check the length of the arguments
  if(strlen(argv[1]) < 1 || strlen(argv[1]) > 2) die(1, "Wrong length of first argument"); 
  if(strlen(argv[2]) != FLAG_BASE64_LEN) die(1, "Wrong length of second argument"); 

  // Check that arguments contain only legal chars
  if(strspn(argv[1], VALID_NUMS) != strlen(argv[1])) die(1, "First argument contains illegal characters");
  if(strspn(argv[2], VALID_BASE64) != FLAG_BASE64_LEN) die(1, "Second argument contains illegal characters");

  // Convert arguments to C++ types.
  teamnum = strtoul(argv[1], &tmp, 10);
  if (!tmp || *tmp != '\0') die(1, "Argument 1 is not a valid integer");
  if(teamnum == 0) die(1, "Argument 1 is 0");
  if(teamnum > 99) die(1, "Argument 1 is greater than 99");
  flagstr = argv[2];

  // everything should be fine now, do the real work
  doIt((uint8_t)teamnum, flagstr);
  if(lock) lock->destroy();
  return 0;
}
