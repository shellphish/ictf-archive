#ifndef __NETWORKOBJECTS_HPP__
#define __NETWORKOBJECTS_HPP__

#include "util.hpp"

class Service;
class ServiceInstance;
class AsyncScript;
class ConfigFile;
class Statefile;

class Team {
  friend class ConfigFile;
public:
  Team(uint8_t num, const string& name, const string& host, const string& cidr);
  
  uint8_t getNum();
  string getName();
  string getHost();
  string getCidr();
  uint8_t getServiceUpCount();

  void addOffensiveScore(uint32_t score);
  void addDefensiveScore(uint32_t score);
  void setPenaltyScore(uint32_t score);

  uint32_t getTotalScore();
  uint32_t getTrendScore();
  void decay();
  void updateState(StateFile* state);
  
  bool is_linked;
private:
  vector<ServiceInstance*> instances;
  uint8_t num;
  string name;
  string host;
  string cidr;
  
  // Scores
  uint32_t offensiveScore;
  uint32_t defensiveScore;
  uint32_t penaltyScore;
  
  // Trend score
  uint32_t trendScore;
  uint32_t lastPenalty;
  int32_t  latestDiffScore;
};

class ServiceInstance {
  friend class ConfigFile;
public:
  ServiceInstance(uint32_t num, Service* service, Team* team, const vector<string>& conf);
  
  enum Statustype {down = 0, up = 1, wrong_flag = 2};
  
  Team* getTeam();
  Service* getService();
  Statustype getStatus();

  void startScore();
  void scoreTimeout();
  void updateState(StateFile* state);
  void setHackers(const string& hackers);
  void addPerServiceScore(uint32_t score);

private:
  uint32_t num;
  Service* service;
  Team* team;
  vector<string> conf;

  // How many offensive points the team has been awarded 
  // by hacking this particular service
  uint32_t perServiceScore;

  Statustype status;
  AsyncScript* script;
  string cookie;
  string hackers;
};

class Service {
  friend class ConfigFile;
public:
  Service (uint8_t num, const string& name, const string& script, float script_to, 
	   uint32_t defensivescore,  uint32_t offensivescore, uint32_t pittyscore,
	   float roundlength, uint32_t validityperiod, uint32_t maxscore);

  uint8_t getNum();
  string getName();
  uint32_t getMaxscore();
  void addServiceInstance(ServiceInstance* s);
  bool validateTeams();
  bool validateScripts();
  float getRoundlength();
  string getScript();
  float getScriptTO();
  const vector <ServiceInstance*> getServiceInstances();
  uint32_t getRoundNb();
  void endOfRound();
  
  bool initial;

private:
  string getFullScriptPath(const string& path);

  uint8_t num;
  string name;
  string script;
  float  script_to;
  uint32_t defensivescore;
  uint32_t offensivescore;
  uint32_t pittyscore;
  float roundlength;
  uint32_t validityperiod;
  uint32_t maxscore;
  uint32_t roundNb;
  
  vector <ServiceInstance*> instances;
};

class NetworkUsage {
public:
  NetworkUsage(string script, float roundlength, float penalty);
  ~NetworkUsage();
  void startScript();
  void scriptTimeout();
  bool isRunning();
  float getRoundlength();
  bool validateScripts();

private:
  vector<string> split(const string& s);
  string getFullScriptPath(const string& path);
  string scriptfilename;
  AsyncScript* script;
  float roundlength;
  float penalty;
  bool running;
};


#endif
