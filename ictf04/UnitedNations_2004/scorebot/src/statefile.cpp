#include "statefile.hpp"
#include "tokenizer.hpp"

StateFile::StateFile(const string& filename, bool init){
  this->filename = filename;
  
  if(init) {
    ofstream out(filename.c_str());
    if (!out.good()) {
      throw StateFileException("Could not create statefile: ").append(filename);
    }
    out.close();
  }

  ifstream in(filename.c_str());
  if (!in.good()) {
    throw StateFileException("Could not open statefile: ").append(filename);
  }

  Tokenizer tok(&in);
  
  while (tok.eat()) {
    string token = tok.getToken();
    if(token == "services") parseServices(tok);
    else if (token == "teams") parseTeams(tok);
    else if (token == "instances") parseInstances(tok);
    else  throw StateFileException("Parse error: unknown token ").append(token);
    token = tok.getToken();
    if(token != "}") throw StateFileException("Parse error");
  }
  
  in.close();
}

void StateFile::parseServices(Tokenizer& tok) {
  string token;
  if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
  if(tok.getToken() != "{") throw StateFileException("Parse error: Expected '{'");
  if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
  token = tok.getToken();
  while (token != "}") {
    string name;
    unsigned long round;
    char* tptr;

    name = tok.getToken();
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    round = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0' || round > 65535) {
      throw StateFileException("Parse error: illegal round number ").append(tok.getToken());
    }
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    if(tok.getToken() != ";") throw StateFileException("Parse error: Expected ';'");
    
    ServiceState state(name, (uint16_t)round);
    serviceStates.push_back(state);

    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    token = tok.getToken();
  }
}

void StateFile::parseTeams(Tokenizer& tok) {
  string token;
  if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
  if(tok.getToken() != "{") throw StateFileException("Parse error: Expected '{'");
  if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
  token = tok.getToken();
  while (token != "}") {
    string name;
    unsigned long totalScore;
    unsigned long trendScore;
    unsigned long offensiveScore;
    unsigned long defensiveScore;
    unsigned long penaltyScore;
    unsigned long lastPenalty;
    long latestDiffScore;
    char* tptr;

    name = tok.getToken();
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    totalScore = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal total score").append(tok.getToken());
    }
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    trendScore = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal trend score").append(tok.getToken());
    }
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    offensiveScore = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal offensive score").append(tok.getToken());
    }
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    defensiveScore = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal defensive score").append(tok.getToken());
    }
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    penaltyScore = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal penalty score").append(tok.getToken());
    }
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    lastPenalty = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal last penalty").append(tok.getToken());
    }
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    latestDiffScore = strtol(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal latest diff score").append(tok.getToken());
    }
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    if(tok.getToken() != ";") throw StateFileException("Parse error: Expected ';'");
    
    TeamState state(name, (uint32_t)totalScore, (uint32_t)trendScore,
		    (uint32_t)offensiveScore, (uint32_t)defensiveScore, (uint32_t)penaltyScore, 
		    (uint32_t)lastPenalty, (int32_t)latestDiffScore);
    teamStates.push_back(state);
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    token = tok.getToken();
  }
}

void StateFile::parseInstances(Tokenizer& tok) {
  string token;
  if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
  if(tok.getToken() != "{") throw StateFileException("Parse error: Expected '{'");
  if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
  token = tok.getToken();
  while (token != "}") {
    string teamname;
    string servicename;
    ServiceInstanceState::Statustype status;
    string cookie;
    string hackers;
    unsigned long perservicescore;
    bool maxedout;
    char* tptr = NULL;

    teamname = tok.getToken();

    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    servicename = tok.getToken();

    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    token = tok.getToken();
    if(token == "down") {
      status =  ServiceInstanceState::down;
    }
    else if (token == "up") {
      status =  ServiceInstanceState::up;
    }
    else if (token == "wrong_flag") {
      status =  ServiceInstanceState::wrong_flag;
    }
    else {
      throw StateFileException("Unknown status: ").append(token);
    }
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    cookie = tok.getToken();
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    hackers = tok.getToken();
   
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    token = tok.getToken();
    perservicescore = strtoul(token.c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') {
      throw StateFileException("Parse error: illegal per-team score").append(token);
    }

    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    token = tok.getToken();
    if(token == "1") maxedout = true;
    else if (token == "0") maxedout = false;
    else  throw StateFileException("Unknown maxOut code: ").append(token);
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    if(tok.getToken() != ";") throw StateFileException("Parse error: Expected ';'");
    
    ServiceInstanceState state(teamname, servicename, status, cookie, hackers, (uint32_t)perservicescore, maxedout);
    instanceStates.push_back(state);
    
    if(!tok.eat()) throw StateFileException("Parse error: premature EOF");
    token = tok.getToken();
  }
}


void StateFile::updateTeam(uint8_t teamno, uint32_t totalScore, uint32_t trendScore,
			   uint32_t offensiveScore, uint32_t defensiveScore, uint32_t penaltyScore,
			   uint32_t lastPenalty, int32_t  latestDiffScore) {
  if(teamno > teamStates.size() || teamno == 0) throw StateFileException("Trying to update nonexistent team");
  teamStates[teamno-1].totalScore = totalScore;
  teamStates[teamno-1].trendScore = trendScore;
  teamStates[teamno-1].offensiveScore = offensiveScore;
  teamStates[teamno-1].defensiveScore = defensiveScore;
  teamStates[teamno-1].penaltyScore = penaltyScore;
  teamStates[teamno-1].lastPenalty = lastPenalty;
  teamStates[teamno-1].latestDiffScore = latestDiffScore;  
}

void  StateFile::updateService(uint8_t serviceno, uint16_t roundNb) {
  if(serviceno > serviceStates.size() || serviceno == 0) throw StateFileException("Trying to update nonexistent team");
  serviceStates[serviceno-1].roundNb = roundNb;
}

void StateFile::updateInstance(uint32_t instanceno, ServiceInstanceState::Statustype status, 
			       const string& cookie, const string& hackers, 
			       uint32_t  perServiceScore, bool maxedOut) {
  if (instanceno > instanceStates.size() || instanceno == 0)  throw StateFileException("Trying to update nonexistent instance");
  
  instanceStates[instanceno-1].status = status;
  instanceStates[instanceno-1].cookie = cookie;
  instanceStates[instanceno-1].hackers = hackers;
  instanceStates[instanceno-1].perServiceScore = perServiceScore;
  instanceStates[instanceno-1].maxedOut = maxedOut;
  
}

void StateFile::addTeam(const string& teamname){
  TeamState s(teamname, 0, 0, 0, 0, 0, 0, 0);
  teamStates.push_back(s);
}

void StateFile::addService(const string& servicename){
  ServiceState s(servicename, 1);
  serviceStates.push_back(s);
}

void StateFile::addServiceInstance(const string& teamname, const string& servicename) {
  ServiceInstanceState i(teamname, servicename, ServiceInstanceState::down, "", "", 0, false);
  instanceStates.push_back(i);
}

void  StateFile::save() {
  ofstream out(filename.c_str());
  if (!out.good()) {
    throw StateFileException("Could not open statefile for writing: ").append(filename);
  }
  
  out << "teams {\n";
  for (vector<TeamState>::iterator i = teamStates.begin(); i!=teamStates.end(); i++) {
    out << "   " << Tokenizer::quoteString((*i).name) << " " << (*i).totalScore << " " << (*i).trendScore << " " <<
      (*i).offensiveScore << " " << (*i).defensiveScore << " " << (*i).penaltyScore << " " <<
      (*i).lastPenalty << " " << (*i).latestDiffScore << ";\n";
  }
  out << "}\n\n";
  
  out << "services {\n";
  for (vector<ServiceState>::iterator i = serviceStates.begin(); i!=serviceStates.end(); i++) {
    out << "   " << Tokenizer::quoteString((*i).name) << " " << (*i).roundNb << ";\n";
  }
  out << "}\n\n";
  
  
  out << "instances {\n";
  for (vector<ServiceInstanceState>::iterator i = instanceStates.begin(); i!=instanceStates.end(); i++) {
    out << "   " << Tokenizer::quoteString((*i).teamname) << " "  <<  Tokenizer::quoteString((*i).servicename) << " ";
    switch ((*i).status) {
    case ServiceInstanceState::down:
      out << "down ";
      break;
    case ServiceInstanceState::up:
      out << "up ";
      break;
    case ServiceInstanceState::wrong_flag:
      out << "wrong_flag ";
      break;
    default:
      out << "??? ";
    }
    out << Tokenizer::quoteString((*i).cookie) <<  " " << Tokenizer::quoteString((*i).hackers);
    out << " " << (*i).perServiceScore << " " << (*i).maxedOut <<  ";\n"; 
  }
  out << "}\n\n";
  
  out.close();
}
