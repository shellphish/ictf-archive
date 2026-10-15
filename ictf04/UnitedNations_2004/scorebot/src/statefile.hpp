#ifndef __STATEFILE_HPP__
#define __STATEFILE_HPP__

#include <stdint.h>

#include <string>
#include <vector>
using namespace std;

class StateFileException {
public:
  StateFileException(const string& msg) {
    this->msg = msg;
  }
  
  string toString() {
    return msg;
  }
  
  StateFileException append(const string& msg) {
    this->msg.append(msg);
    return *this;
  }

protected:
  string msg;
};

class ServiceState {
public:
  ServiceState(const string& name, uint16_t roundNb) {
    this->name = name;
    this->roundNb = roundNb;
  }
  
  string name;
  uint16_t roundNb;
};

class TeamState {
public:
  TeamState(const string& name, uint32_t totalScore, uint32_t trendScore, 
	    uint32_t offensiveScore, uint32_t defensiveScore, uint32_t penaltyScore,
	    uint32_t lastPenalty, int32_t  latestDiffScore) {
    this-> name = name;
    this->totalScore = totalScore;
    this->trendScore = trendScore;
    this->offensiveScore = offensiveScore;
    this->defensiveScore = defensiveScore;
    this->penaltyScore = penaltyScore;
    this->lastPenalty = lastPenalty;
    this->latestDiffScore = latestDiffScore;
  }
  
  string name;
  uint32_t totalScore;
  uint32_t trendScore;
  uint32_t offensiveScore;
  uint32_t defensiveScore;
  uint32_t penaltyScore;
  uint32_t lastPenalty;
  int32_t  latestDiffScore;
};


class ServiceInstanceState {
public:
  enum Statustype {down = 0, up = 1, wrong_flag = 2};
  ServiceInstanceState(const string& teamname, const string& servicename, 
		       Statustype status, string cookie, string hackers,  
		       uint32_t  perServiceScore, bool maxedOut) {
    this->teamname = teamname;
    this->servicename = servicename;
    this->status = status;
    this->cookie = cookie;
    this->hackers = hackers;
    this->perServiceScore = perServiceScore;
    this->maxedOut = maxedOut;
  }


  string teamname;
  string servicename;
  Statustype status;
  string cookie;
  string hackers;
  uint32_t perServiceScore;
  bool maxedOut;
};


class Tokenizer;

class StateFile {
public:
  StateFile(const string& filename, bool init = false);
  vector<ServiceState> getServiceStates() { return serviceStates; }
  vector<TeamState> getTeamStates() { return teamStates; }
  vector<ServiceInstanceState> getInstances() { return instanceStates; }
  void updateTeam(uint8_t teamno, uint32_t totalScore, uint32_t trendScore,
		  uint32_t offensiveScore, uint32_t defensiveScore, uint32_t penaltyScore,
		  uint32_t lastPenalty, int32_t  latestDiffScore);
  void updateService(uint8_t serviceno, uint16_t roundNb);
  void updateInstance(uint32_t instanceno, ServiceInstanceState::Statustype status, 
		      const string& cookie, const string& hackers, 
		      uint32_t  perServiceScore, bool maxedOut);
  void addTeam(const string& teamname);
  void addService(const string& servicename);
  void addServiceInstance(const string& teamname, const string& servicename);
  void save();

protected:
  void parseServices(Tokenizer& tok);
  void parseTeams(Tokenizer& tok);
  void parseInstances(Tokenizer& tok);

  string filename;
  vector<ServiceState> serviceStates;  
  vector<TeamState> teamStates;
  vector<ServiceInstanceState> instanceStates;
};

#endif
