#ifndef __SCOREBOTCONF_HPP__
#define __SCOREBOTCONF_HPP__

#include "util.hpp"

class Tokenizer;
class Service;
class Team;
class ServiceInstance;
class NetworkUsage;

class ConfigFile {
public:
  ConfigFile(const string& filename);
  bool parse(bool initFiles);
  bool restoreState();

  vector<Service*> getServices();
  vector<Team*> getTeams();
  vector<ServiceInstance*> getServiceInstances();
  NetworkUsage* getNetworkUsage();

private:
  bool initState();
  bool parseTeam(const string& name, Tokenizer& tok);
  bool parseService(const string& name, Tokenizer& tok);
  bool parseGlobals(Tokenizer& tok, bool init_files);
  bool parseNetworkUse(Tokenizer& tok);
  void parseError(Tokenizer& tok);

  class ServiceMapping{
  public:
    ServiceMapping(const string& servicename,const string&  teamname,
                const vector<string>& conf) {
      this->servicename = servicename;
      this->teamname = teamname;
      this->conf = conf;
    }
    string servicename;
    string teamname;
    string flag;
    vector<string> conf;
  };

  string filename;
  vector<Service*> services;
  vector<Team*> teams;
  NetworkUsage* networkusage;
  vector<ServiceInstance*> serviceInstances;
  vector<ServiceMapping*> servicemappings;
  uint8_t currentTeam;
  uint8_t currentService;
};

#endif
