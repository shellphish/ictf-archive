#include "util.hpp"

#define DEFAULT_SCRIPTDIR "/etc/scorebot.d/"
#define DEFAULT_LOGFILE   "/var/log/scorebot"
#define DEFAULT_PIDFILE   "/var/run/scorebot.pid"
#define DEFAULT_STATEFILE "/var/run/scorebot.state"
#define DEFAULT_FLAGLOG   "/var/run/scorebot.flaglog"
#define DEFAULT_DECAYTIME 120
#define DEFAULT_DECAYFACTOR .99

Log::Log(string filename) {
  logfile = filename;
  if(logfile != "") {
    open(filename.c_str(), ofstream::app);
  }
  else {
    open("/dev/null", ofstream::app);
  }
}

#define TIMESTR_SIZE 30

ofstream& Log::log() {
  time_t epoch_time = time(NULL);
  struct tm local_time;
  localtime_r(&epoch_time, &local_time);
  char timestr[TIMESTR_SIZE + 1];
  strftime(timestr, TIMESTR_SIZE, "[%B %d %T] ", &local_time);

  (*this) << timestr;
  return (*this);
}


Globals::Globals() {
  logfile = DEFAULT_LOGFILE;
  tracefile = "";
  scriptdir = DEFAULT_SCRIPTDIR;
  pidfile = DEFAULT_PIDFILE;
  statefile = NULL;
  flaglog = NULL;
  lockfile = NULL;
  decaytime = DEFAULT_DECAYTIME;
  decayfactor = DEFAULT_DECAYFACTOR;
  log = NULL;
  trace = NULL;
  fractionmode = false;
  terminate = false;
}


Log* Globals::getLog() {
  if (!log) log = new Log(logfile);
  return log;
}

Log* Globals::getTrace() {
  if (!trace) trace = new Log(tracefile);
  return trace;
}

string Globals::getScriptdir() {
  return scriptdir;
}

string Globals::getPidfile() {
  return pidfile;
}

StateFile* Globals::getStatefile() {
  return statefile;
}

FlagLog* Globals::getFlaglog() {
  return flaglog;
}

LockFile* Globals::getLockfile() {
  return lockfile;
}

string Globals::getSecretkey() {
  return secretkey;
}


float Globals::getDecaytime() {
  return decaytime;
}

float Globals::getDecayfactor() {
  return decayfactor;
}

bool Globals::getFractionmode() {
  return fractionmode;
}

bool Globals::getTerminate() {
  return terminate;
}

void Globals::setTerminate() {
  terminate = true;
}

vector<Team*> Globals::getTeams() {
  return teams;
}

vector<Service*> Globals::getServices() {
  return services;
}

Globals* Globals::instance = NULL;

Globals* Globals::get() {
  if (!instance) instance = new Globals();
  return instance;
}
