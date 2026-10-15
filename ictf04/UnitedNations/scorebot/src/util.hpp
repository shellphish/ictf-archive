#ifndef __UTIL_HPP__
#define __UTIL_HPP__

#include <stdint.h>

#include <string>
#include <fstream>
#include <vector>

#include <iostream>

using namespace std;


#define LOG(msg) (*(Globals::get()->getLog())).log() << msg << endl;
#define TRACE(msg) (*(Globals::get()->getTrace())).log() << msg << endl;

class CTFConfigFile;
class StateFile;
class FlagLog;
class LockFile;
class Team;
class Service;

class Log : public ofstream{
public:
  Log(string filename);

  ofstream& log();

private:
  string logfile;
};

class Globals {
  friend class ConfigFile;
public:
  static Globals* get();

  Log* getLog();
  Log* getTrace();
  string getScriptdir();
  string getPidfile();
  StateFile* getStatefile();
  FlagLog* getFlaglog();
  LockFile* getLockfile();
  string getSecretkey();

  float getDecaytime();
  float getDecayfactor();
  bool getFractionmode();
  bool getTerminate();
  void setTerminate();
  vector<Team*> getTeams();
  vector<Service*> getServices();

private:
  static Globals* instance;

  Log* log;
  Log* trace;
  string logfile;
  string tracefile;
  string scriptdir;
  string pidfile;
  string secretkey;
  float  decaytime;
  float  decayfactor;
  bool fractionmode;
  bool terminate;

  StateFile* statefile;
  FlagLog*   flaglog;
  LockFile*  lockfile;
  vector<Team*> teams;
  vector<Service*> services;

  Globals();
};



#endif
