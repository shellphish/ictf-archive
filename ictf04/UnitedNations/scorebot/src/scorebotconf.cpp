#include "scorebotconf.hpp"
#include "tokenizer.hpp"
#include "networkobjects.hpp"
#include "lockfile.hpp"
#include "flaglog.hpp"
#include "statefile.hpp"

#define DO_EAT  if (!tok.eat()) {\
                  parseError(tok);  \
                  return false;  \
                }


ConfigFile::ConfigFile(const string& filename){
  this->filename = filename;
  currentTeam = 0;
  currentService = 0;
  networkusage = NULL;
}


bool ConfigFile::parse(bool initfiles){
  uint32_t currentInstance = 1;
  ifstream in(filename.c_str());

  if (!in.good()) {
    cerr << "Could not open configfile (" << filename << ")" << endl;
    return false;
  }

  Tokenizer tok(&in);

  while (tok.eat()) {
    string token = tok.getToken();
    if(token == "service") {
      DO_EAT;
      string servicename = tok.getToken();
      DO_EAT;
      if(tok.getToken() != "{") {
        parseError(tok);
        return false;
      }
      DO_EAT;
      if(currentService == 255) {
	cerr << "Max number of services is 255\n";
	return false;
      }
      currentService++;
      if(!parseService(servicename, tok)) return false;
    }
    else if (token == "team") {
      DO_EAT;
      string teamname = tok.getToken();
      DO_EAT;
      if(tok.getToken() != "{") {
        parseError(tok);
        return false;
      }
      DO_EAT;
      if(currentTeam == 255) {
	cerr << "Max number of teams is 255\n";
	return false;
      }
      currentTeam++;
      if(!parseTeam(teamname, tok)) return false;
    }
    else if (token == "global") {
      DO_EAT;
      if(tok.getToken() != "{") {
        parseError(tok);
        return false;
      }
      DO_EAT;
      if(!parseGlobals(tok, initfiles)) return false;
    }
    else if (token == "networkusage") {
      DO_EAT;
      if(tok.getToken() != "{") {
        parseError(tok);
        return false;
      }
      DO_EAT;
      if(!parseNetworkUse(tok)) return false;
    }
    else if (token == "web") {
      while (token != "}") {
	DO_EAT;
	token = tok.getToken();
      }
    }
    else {
      parseError(tok);
      return false;
    }
  }
  
    // Now, link services to hosts and create service instance objects
  for ( vector<ServiceMapping*>::iterator i = servicemappings.begin(); i != servicemappings.end(); i++) {
    ServiceMapping* f = *i;
    Service* s = NULL;
    Team* t = NULL;
    for( vector<Service*>::iterator j = services.begin(); j!= services.end(); j++) {
      if ((*j)->getName() == f->servicename) {
        s = *j;
        break;
      }
    }

    for( vector<Team*>::iterator j = teams.begin(); j!= teams.end(); j++) {
      if ((*j)->getName() == f->teamname) {
        t = *j;
        break;
      }
    }

    if (!t) {
      cerr << "Internal error, team " << f->teamname << " does not exist" << endl;
      return false;
    }
    if (!s) {
      cerr << "In team " << f->teamname << " nonexistent service " <<  f->servicename << endl;
      return false;
    }

    ServiceInstance* si = new ServiceInstance(currentInstance++, s, t, f->conf);
    s->addServiceInstance(si);
    t->instances.push_back(si);
    serviceInstances.push_back(si);

    delete f;
  }
  
  servicemappings.clear();
  
  // Now create service instances for teams that did not specify conf.
  for( vector<Service*>::iterator i = services.begin(); i!= services.end(); i++) {
    if (!(*i)->validateTeams()) return false;

    for( vector<Team*>::iterator j = teams.begin(); j!= teams.end(); j++) {
      if (!(*j)->is_linked) {
	vector<string> emptyconf;
	ServiceInstance* si = new ServiceInstance(currentInstance++, *i, *j, emptyconf);
	(*i)->addServiceInstance(si);
	(*j)->instances.push_back(si);
	serviceInstances.push_back(si);
      }
      (*j)->is_linked = false;
    }
  }

  // And validate all the scripts
  for( vector<Service*>::iterator i = services.begin(); i!= services.end(); i++) {
    if (!(*i)->validateScripts()) return false;
  }
  
  if(networkusage && !networkusage->validateScripts()) return false;

  Globals::get()->teams = teams;
  Globals::get()->services = services;
  
  if(initfiles) return initState();
  else return true;
}

bool ConfigFile::restoreState() {
  StateFile* state = Globals::get()->getStatefile();
  if(!state) {
    cerr <<"Internal error, statefile is NULL\n";
    return false;
  }

  vector<ServiceState> serviceStates = state->getServiceStates();
  if(serviceStates.size() != services.size()) {
    cerr << "Service state does not match configfile (length)\n";
    return false;
  }
  
  for (vector<Service*>::size_type i=0; i< services.size(); i++) {
    Service* s = services[i];
    ServiceState ss =  serviceStates[i];
    if(s->name != ss.name) {
      cerr << "Service state does not match configfile (order)\n";
      return false;
    }
    s->roundNb = ss.roundNb;
  }
  
  vector<TeamState> teamStates = state->getTeamStates();
  
  if(teamStates.size() != teams.size()) {
    cerr << "Team state does not match configfile (length)\n";
    return false;
  }
  
  for (vector<Team*>::size_type i=0; i< teams.size(); i++) {
    Team* t = teams[i];
    TeamState ts =  teamStates[i];
    if(t->name != ts.name) {
      cerr << "Team state does not match configfile (order)\n";
      return false;
    }
    t->offensiveScore = ts.offensiveScore;
    t->defensiveScore = ts.defensiveScore;
    t->penaltyScore = ts.penaltyScore;
    t->trendScore = ts.trendScore;
    t->lastPenalty = ts.lastPenalty;
    t->latestDiffScore = ts.latestDiffScore;
  }
  
  vector<ServiceInstanceState> instanceStates = state->getInstances();
  
  if(instanceStates.size() != serviceInstances.size()) {
    cerr << "Instance state does not match configfile (length)\n";
    return false;
  }

  for (vector<ServiceInstance*>::size_type i=0; i < instanceStates.size(); i++) {
    ServiceInstance* si = serviceInstances[i];
    ServiceInstanceState sit = instanceStates[i];
    
    if(si->getTeam()->getName() != sit.teamname ||
       si->getService()->getName() != sit.servicename) {
      cerr << "Instance state does not match configfile (order)\n";
      return false;
    }
    
    si->cookie = sit.cookie;
    si->perServiceScore = sit.perServiceScore;
    // Remember to keep the two different status enums equal!
    si->status = (ServiceInstance::Statustype)sit.status; // Should we copy status? I do't think it matters
  }

  return true;
}


vector<Service*> ConfigFile::getServices(){
  return services;
}

vector<Team*> ConfigFile::getTeams(){
  return teams;
}

vector<ServiceInstance*> ConfigFile::getServiceInstances(){
  return serviceInstances;
}

NetworkUsage* ConfigFile::getNetworkUsage() {
  return networkusage;
}


bool ConfigFile::initState() {
  StateFile* state = Globals::get()->getStatefile();
  if(!state) {
    cerr <<"Internal error, statefile is NULL\n";
    return false;
  }
  
  for( vector<Service*>::iterator i = services.begin(); i!= services.end(); i++) {
    state->addService((*i)->getName());
  }
  for( vector<Team*>::iterator i = teams.begin(); i!= teams.end(); i++) {
    state->addTeam((*i)->getName());
  }
  for( vector<ServiceInstance*>::iterator i = serviceInstances.begin(); i!= serviceInstances.end(); i++) {
    state->addServiceInstance((*i)->getTeam()->getName(), (*i)->getService()->getName());
  }


  try {
    Globals::get()->getLockfile()->lock();
    state->save();
    Globals::get()->getLockfile()->unlock();
  }
  catch (StateFileException e) {
    cerr << "Error writing statefile: " << e.toString() << endl;
    return false;
  }
  catch (LockFileException e) {
    cerr << "Error locking file: " << e.toString() << endl;
    return false;
  }
  return true;
}

bool ConfigFile::parseTeam(const string& name, Tokenizer& tok) {
  string host = "";
  string cidr = "";

  string token = tok.getToken();
  while (token != "}") {
    if (token == "host"){
      DO_EAT;
      host = tok.getToken();
      DO_EAT;
    }
    else if (token == "cidr"){
      DO_EAT;
      cidr = tok.getToken();
      DO_EAT;
    }
    else if (token == "conf"){
      DO_EAT;
      string servicename = tok.getToken();
      DO_EAT;
      vector<string> conf;
      token = tok.getToken();
      while (token != ";") {
	conf.push_back(token);
	DO_EAT;
	token = tok.getToken();
      }
      servicemappings.push_back(new ServiceMapping(servicename, name, conf));
    }
    else {
      cerr << "Unexpected keyword: " << token << " in " << name << " team section" << endl;
      return false;
    }
    token = tok.getToken();
    if(token != ";") {
      parseError(tok);
      return false;
    }
    DO_EAT;
    token = tok.getToken();
  }
  
  // Check for mandatory values
  if (host == "" || cidr == "") {
    cerr << "Mandatory value missing in team " << name << endl;
    return false;
  }

  Team* t = new Team(currentTeam, name, host, cidr);
  teams.push_back(t);

  return true;
}


bool ConfigFile::parseService(const string& name, Tokenizer& tok) {
  string script = "";
  string script_to = "";
  string defensivescore = "";
  string offensivescore = "";
  string pittyscore = "";
  string roundlength = "";
  string validityperiod = "";
  string maxscore = "";

  string token = tok.getToken();
  while (token != "}") {
    if (token == "script"){
      DO_EAT;
      script = tok.getToken();
      DO_EAT;
    }
    else if (token == "timeout"){
      DO_EAT;
      script_to = tok.getToken();
      DO_EAT;
    }
    else if (token == "defensivescore"){
      DO_EAT;
      defensivescore = tok.getToken();
      DO_EAT;
    }
    else if (token == "offensivescore"){
      DO_EAT;
      offensivescore = tok.getToken();
      DO_EAT;
    }
    else if (token == "pittyscore"){
      DO_EAT;
      pittyscore = tok.getToken();
      DO_EAT;
    }
    else if (token == "roundlength"){
      DO_EAT;
      roundlength = tok.getToken();
      DO_EAT;
    }
    else if (token == "validityperiod"){
      DO_EAT;
      validityperiod = tok.getToken();
      DO_EAT;
    }
    else if(token == "maxscore") {
      DO_EAT;
      maxscore = tok.getToken();
      DO_EAT;
    }
    else {
      cerr << "Unexpected keyword: " << token << " in " << name << " service section" << endl;
      return false;
    }
    token = tok.getToken();
    if(token != ";") {
      parseError(tok);
      return false;
    }
    DO_EAT;
    token = tok.getToken();
  }

  // Check for mandatory values
  if (script == "" || script_to == "" ||
      defensivescore == "" || offensivescore == "" || roundlength == "" || validityperiod == "") {
    cerr << "Mandatory value missing in service " << name << endl;
    return false;
  }

  // Convert strings to numbers
  float script_to_f = 0;
  uint32_t offensivescore_i = 0;
  uint32_t defensivescore_i = 0;
  uint32_t pittyscore_i = 0;
  float roundlength_f = 0;
  uint32_t validityperiod_i = 0;
  uint32_t maxscore_i = 0;
  char* tmp;
  
  script_to_f = strtof(script_to.c_str(), &tmp);
  if(!tmp || *tmp) {
    cerr << "Value of timeout is not a number (" <<  script_to << ")" << endl;
    return false;
  }

  offensivescore_i = strtoul(offensivescore.c_str(), &tmp, 0);
  if(!tmp || *tmp) {
    cerr << "Value of offensivescore is not a number (" <<  offensivescore << ")" << endl;
    return false;
  }

  defensivescore_i = strtoul(defensivescore.c_str(), &tmp, 0);
  if(!tmp || *tmp) {
    cerr << "Value of defensivescore is not a number (" <<  defensivescore << ")" << endl;
    return false;
  }

  if(pittyscore != "") {
    pittyscore_i = strtoul(pittyscore.c_str(), &tmp, 0);
    if(!tmp || *tmp) {
      cerr << "Value of pittyscore is not a number (" <<  pittyscore << ")" << endl;
      return false;
    }
  }

  roundlength_f = strtof(roundlength.c_str(), &tmp);
  if(!tmp || *tmp) {
    cerr << "Value of roundlength is not a number (" <<  roundlength << ")" << endl;
    return false;
  }

  validityperiod_i = strtol(validityperiod.c_str(), &tmp, 0);
  if(!tmp || *tmp) {
    cerr << "Value of validityperiod is not a number (" <<  validityperiod << ")" << endl;
    return false;
  }
  
  if (maxscore != "") {
    maxscore_i = strtol(maxscore.c_str(), &tmp, 0);
    if(!tmp || *tmp) {
      cerr << "Value of maxscore is not a number (" <<  maxscore << ")" << endl;
      return false;
    }
  }
  
  
  Service* s = new Service(currentService, name, script, script_to_f, 
			   defensivescore_i, offensivescore_i, pittyscore_i, 
			   roundlength_f, validityperiod_i, maxscore_i);
  services.push_back(s);
  
  return true;
}


bool ConfigFile::parseGlobals(Tokenizer& tok, bool initFiles) {
  Globals* g = Globals::get();
  
  string statefilename;
  string flagfilename;
  
  string token = tok.getToken();
  while (token != "}") {
    if (token == "logfile") {
      DO_EAT;
      g->logfile =  tok.getToken();
      DO_EAT;
    }
    else if (token == "tracefile") {
      DO_EAT;
      g->tracefile =  tok.getToken();
      DO_EAT;
    }
    else if (token == "scriptdir") {
      DO_EAT;
      g->scriptdir =  tok.getToken();
      if (g->scriptdir[g->scriptdir.length()] != '/') g->scriptdir += "/";
      DO_EAT;
    }
    else if (token == "pidfile") {
      DO_EAT;
      g->pidfile =  tok.getToken();
      DO_EAT;
    }
    else if (token == "statefile") {
      DO_EAT;
      statefilename =  tok.getToken();
      DO_EAT;
    }
    else if (token == "flaglog") {
      DO_EAT;
      flagfilename =  tok.getToken();
      DO_EAT;
    }
    else if (token == "secretkey") {
      DO_EAT;
      g->secretkey =  tok.getToken();
      DO_EAT;
    }
   else if (token == "decaytime") {
      DO_EAT;
      char* tmp;
      string decaystring =  tok.getToken();
      g->decaytime =  strtof(decaystring.c_str(), &tmp);
      if(!tmp || *tmp) {
        cerr << "Value of decaytime is not a number (" << decaystring << ")" << endl;
        return false;
      }
      DO_EAT;
    }
    else if (token == "decayfactor") {
      DO_EAT;
      char* tmp;
      string decaystring =  tok.getToken();
      g->decayfactor =  strtof(decaystring.c_str(), &tmp);
      if(!tmp || *tmp) {
        cerr << "Value of decayfactor is not a number" << endl;
        return false;
      }
      DO_EAT;
    }
    else if (token == "offensive_fraction_mode") {
      DO_EAT;
      if (tok.getToken() != "0") {
	g->fractionmode = true;
      }
      DO_EAT;
    }
    else {
      cerr << "Unexpected keyword: " << token << " in global section" << endl;
      return false;
    }
    token = tok.getToken();
    if(token != ";") {
      parseError(tok);
      return false;
    }
    DO_EAT;
    token = tok.getToken();
  }
  
  try {
    g->flaglog = new FlagLog(flagfilename, initFiles);
    g->statefile = new StateFile(statefilename, initFiles);
    g->lockfile = new LockFile(statefilename + ".lock");
    
    g->lockfile->lock();
    g->flaglog->open();
    g->lockfile->unlock();
  }
  catch (FlagLogException e){
    cerr << "Error opening flaglog: " << e.toString() << endl;
    return false;
  }
  catch (StateFileException e) {
    cerr << "Error opening statefile: " << e.toString() << endl;
    return false;
  }
  catch (LockFileException e) {
    cerr << "Error opening lockfile: " << e.toString() << endl;
    return false;
  }

  return true;
}


bool ConfigFile::parseNetworkUse(Tokenizer& tok){
  string script;
  float  roundlength = -1;
  float  penalty = -1;
  
  string token = tok.getToken();
  while (token != "}") {
    if (token == "script") {
      DO_EAT;
      script =  tok.getToken();
      DO_EAT;
    }
    else if (token == "roundlength") {
      DO_EAT;
      char* tmp;
      string roundstring =  tok.getToken();
      roundlength=  strtof(roundstring.c_str(), &tmp);
      if(!tmp || *tmp) {
        cerr << "Value of roundlength is not a number (" << roundstring << ")" << endl;
        return false;
      }
      DO_EAT;
    }
    else if (token == "penalty") {
      DO_EAT;
      char* tmp;
      string penaltystring =  tok.getToken();
      penalty =  strtof(penaltystring.c_str(), &tmp);
      if(!tmp || *tmp) {
        cerr << "Value of penalty is not a number (" << penaltystring << ")" << endl;
        return false;
      }
      DO_EAT;
    }
    else {
      cerr << "Unexpected keyword: " << token << " in networkusage section" << endl;
      return false;
    }
    token = tok.getToken();
    if(token != ";") {
      parseError(tok);
      return false;
    }
    DO_EAT;
    token = tok.getToken();
  }
  
  if(script == "" || roundlength < 0 || penalty < 0) {
    cerr << "Mandatory value missing in networkpenalty section" << endl;
    cerr << "Required values are script, roundlength, and penalty" << endl;
    return false;
  }
  
  if(networkusage) {
    cerr << "Error specified two networkusage sections" << endl;
    return false;
  }
 
  networkusage = new NetworkUsage(script, roundlength, penalty);
  
  return true;
}

void ConfigFile::parseError(Tokenizer& tok) {
  string token =  tok.getToken();
  if (token != "")
    cerr << "Unexpected token: " << tok.getToken() << endl;
  else
    cerr << "Unexpected EOF" << endl;
}
