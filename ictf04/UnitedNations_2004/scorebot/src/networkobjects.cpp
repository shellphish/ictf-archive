#include "networkobjects.hpp"
#include "asyncscript.hpp"
#include "CTFFlag.hpp"
#include "statefile.hpp"
#include "lockfile.hpp"
#include "flaglog.hpp"

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

Team::Team(uint8_t num, const string& name, const string& host, const string& cidr){
  this->num = num;
  this->name = name;
  this->host = host;
  this->cidr = cidr;
  this->offensiveScore = 0;
  this->defensiveScore = 0;
  this->penaltyScore = 0;
  this->trendScore = 0;
  this->lastPenalty = 0;
  this->latestDiffScore = 0;
  this->is_linked = false;
}

uint8_t Team::getNum() {
  return num;
}

string Team::getName() {
  return name;
}

string Team::getHost() {
  return host;
}

string Team::getCidr() {
  return cidr;
}

uint8_t  Team::getServiceUpCount() {
  uint8_t count = 0;
  for (vector<ServiceInstance*>::iterator i = instances.begin(); i!= instances.end(); i++) {
    if ((*i)->getStatus() == ServiceInstance::up) {
      count++;
    }
  }
  return count;
}

void Team::addOffensiveScore(uint32_t score) {
  offensiveScore += score;
  latestDiffScore  += score;
}

void Team::addDefensiveScore(uint32_t score) {
  defensiveScore += score;
  latestDiffScore += score;
}

void Team::setPenaltyScore(uint32_t score) {
  cerr << "Updating score for " << name << " " << score << endl ;

  if(score > (defensiveScore + offensiveScore)){
    score = defensiveScore + offensiveScore;
  }
  penaltyScore = score;

  
  if(penaltyScore < lastPenalty) {
    LOG("ERROR: Penalty score decreased " << lastPenalty << "->" << score << " ("<<name<<")");
  }
  else {
    latestDiffScore -= penaltyScore - lastPenalty;
  }
  lastPenalty = penaltyScore;
}


void Team::decay() {
  trendScore = (uint32_t)(trendScore * Globals::get()->getDecayfactor());
  if(latestDiffScore < 0 && ((uint32_t)-latestDiffScore) > trendScore) {
    trendScore = 0;
  }
  else {
    trendScore += latestDiffScore;
  }
  latestDiffScore = 0;
}

void Team::updateState(StateFile* s) {
  s->updateTeam(num, getTotalScore(), trendScore, 
		offensiveScore, defensiveScore, penaltyScore,
		lastPenalty, latestDiffScore);
}

uint32_t Team::getTotalScore() {
  uint32_t ret = offensiveScore + defensiveScore;
  if (ret < penaltyScore) {
    return 0;
  }
  else {
    return ret - penaltyScore;
  }
}

uint32_t Team::getTrendScore() {
  return trendScore;
}

ServiceInstance::ServiceInstance(uint32_t num, Service* service, Team* team, const vector<string>& conf){
  this->num = num;
  this->team = team;
  this->service = service;
  this->status = down;
  this->conf = conf;
  this->script = NULL;
  this->perServiceScore = 0;
}

Team* ServiceInstance::getTeam() {
  return team;
}

Service* ServiceInstance::getService() {
  return service;
}

ServiceInstance::Statustype ServiceInstance::getStatus() {
  return status;
}


void  ServiceInstance::startScore() {
  if(script) {
    LOG("Error starting a script that is running already(" << team->getName() << "." << service->getName() << ")");
    try {
      script->stop();
    }
    catch (AsyncScriptException e) {
      LOG("Caught exception when stopping script: " << e.toString() <<" (" << team->getName() << "." << service->getName() << ")");
    }
  }
  
  TRACE("Started scoring for (" << team->getName() << "." << service->getName() << ")");

  vector<string> args;
  args.push_back(team->getHost());
  try {
    CTFFlag flag(team->getNum(), service->getNum(), service->getRoundNb(), Globals::get()->getSecretkey());
    args.push_back(flag.toString()); // Flag
  } catch (FlagException e) {
    LOG("Error getting flag ("  << team->getName() << "." << service->getName() << ")");
    return;
  }
  args.push_back(cookie);
  args.insert(args.end(), conf.begin(), conf.end());
  
  try {
    if(script) {
      delete script;
    }
    script = new AsyncScript(service->getScript(), args);
    script->run();    
  } catch (AsyncScriptException e) {
    LOG("Error starting script, exception:" << e.toString() << " (" << 
	team->getName() << "." << service->getName() << ")");
  } 
}

void  ServiceInstance::scoreTimeout() {
  TRACE("Getting scores for (" << team->getName() << "." << service->getName() << ")");
  status = down;
  try {
    if(script == NULL) {
      LOG("Error timing out script, script not started (" << team->getName() << "." << service->getName() << ")");
    } else if(!script->stop()) {
      LOG("Script timed out (" << team->getName() << "." << service->getName() << ")");
    }
    else if (!script->resultReady()) {
      LOG("Error, script result not ready (" << team->getName() << "." << service->getName() << ")");
    }
    else if (script->getExitcode() != 0) {
      LOG("Error, script returned exitcode: " << script->getExitcode() << " (" << 
	team->getName() << "." << service->getName() << ")");
    }
    else {
      // Everything is fine now, parse output of script.
      string retstring = script->getStdout();
      TRACE("Script says ("  << team->getName() << "." << service->getName() << "):" << retstring);

      string ret_flag;
      string ret_cookie;
      // Parse out return arguments
      string::size_type ptr = 0;
      while (ptr != string::npos) {
	string::size_type ptr2 = retstring.find("\n", ptr);
	if(retstring.compare(ptr, 5, "FLAG:") == 0) {
	  ptr += 5;
	  if (ptr2 != string::npos) {
	    ret_flag = retstring.substr(ptr, ptr2 - ptr);
	  }
	  else {
	    ret_flag = retstring.substr(ptr);
	  }
	}
	else if (retstring.compare(ptr, 7, "COOKIE:") == 0) {
	  ptr += 7;
	  if(ptr2 != string::npos) {
	    ret_cookie = retstring.substr(ptr, ptr2 - ptr);
	  }
	  else {
	    ret_cookie = retstring.substr(ptr);
	  }
	}
	ptr = (ptr2 == string::npos) ? ptr2 : ptr2 + 1;
      }
      
      LOG("Flag is (" << team->getName() << "." << service->getName() << "): " << ret_flag << " Cookie is: " << ret_cookie);
      cookie = ret_cookie;
      
      // Check flag
      if (ret_flag.size() == FLAG_BASE64_LEN) {
	try {
	  CTFFlag flag(ret_flag, Globals::get()->getSecretkey());
	  if(flag.getTeamNum() != team->getNum()) {
	    status = wrong_flag;
	    LOG("Invalid flag: " << ret_flag << "Wrong team number" << " (" << team->getName() << "." << service->getName() << ")" );
	  }
	  else if(flag.getServiceNum() != service->getNum()) {
	    status = wrong_flag;
	    LOG("Invalid flag: " << ret_flag << "Wrong service number" << " (" << team->getName() << "." << service->getName() << ")" );
	  }
	  else if (flag.getGeneration() !=  service->getRoundNb() - 1) {
	    status = wrong_flag;
	    LOG("Invalid flag: " << ret_flag << "Wrong generation number" << " (" << team->getName() << "." << service->getName() << ")");
	  }
	  else {
	    status = up;
	    LOG("Flag OK (" << team->getName() << "." << service->getName() << ")" );
	  }
	} catch (FlagException e) {
	  status = wrong_flag;
	  LOG("Invalid flag: " << ret_flag << " (" << e.toString() << ") (" << team->getName() << "." << service->getName() << ")" );
	}
      }
      else if (ret_flag.size() == 0) {
	LOG("No flag (" << team->getName() << "." << service->getName() << ")");
      }
      else {
	status = wrong_flag;
	LOG("Wrong flag length: (" << ret_flag << ") (" << team->getName() << "." << service->getName() << ")" );
      }
    }
  }
  catch (AsyncScriptException e) {
    LOG("Error stopping script, exception (" << team->getName() << "." << service->getName() << "):" << e.toString());
  }
  if(script) {
    delete script;
    script = NULL;
  }
}


void ServiceInstance::updateState(StateFile* state) {
  state->updateInstance(num, (ServiceInstanceState::Statustype)status, cookie, 
			hackers, perServiceScore, (perServiceScore >= service->getMaxscore()));
}

void ServiceInstance::setHackers(const string& hackers) {
  this->hackers = hackers;
}

void ServiceInstance::addPerServiceScore(uint32_t score) {
  perServiceScore += score;
}

Service::Service(uint8_t num, const string& name, const string& script, float script_to, 
		 uint32_t defensivescore,  uint32_t offensivescore, uint32_t pittyscore,
		 float roundlength, uint32_t validityperiod, uint32_t maxscore){
  this->num = num;
  this->name = name;
  this->script = getFullScriptPath(script);
  this->script_to = script_to;
  this->defensivescore = defensivescore;
  this->offensivescore = offensivescore;
  this->pittyscore =  pittyscore;
  this->roundlength = roundlength;
  this->validityperiod  = validityperiod;
  this->maxscore = maxscore;
  this->roundNb = 1;
  this->initial = true;
}

uint8_t Service::getNum() {
  return num;
}

string Service::getName() {
  return name;
}

uint32_t Service::getMaxscore() {
  return maxscore;
}

void Service::addServiceInstance(ServiceInstance* s) {
  instances.push_back(s);
}

bool Service::validateTeams(){
  for (vector<ServiceInstance*>::iterator i = instances.begin(); i != instances.end(); i++) {
    if (!(*i)|| !(*i)->getTeam()) {
      cerr << "Internal linking error in service " << name << endl;
      return false;
    }
    Team* t = (*i)->getTeam();
    
    if(t->is_linked) {
      cerr << "Team " << t->getName() <<
        " has specified service " << name << " more than once" << endl;
      return false;
    }
    t->is_linked = true;
  }
  return true;
}

bool Service::validateScripts(){
  struct stat s;
  if (stat(script.c_str(), &s) != 0) {
    cerr << "Cannot access script " << script << endl;
    return false;
  }
  if (  (s.st_mode & S_IXOTH) == 0) {
    cerr << "Script " << script << " is not executable" << endl;
    return false;
  }

  if(script_to >= roundlength) {
    cerr << "Script timeout is greater than the round length" << endl;
    return false;
  }
  
  return true;
}


float Service::getRoundlength() {
  return roundlength;
}

float Service::getScriptTO() {
  return script_to;
}

string Service::getScript() {
  return script;
}



const vector <ServiceInstance*> Service::getServiceInstances() {
  return instances;
}

uint32_t  Service::getRoundNb() {
  return roundNb;
}

void  Service::endOfRound() {
  StateFile* state = Globals::get()->getStatefile();
  FlagLog* flog = Globals::get()->getFlaglog();
  LockFile* lock = Globals::get()->getLockfile();
  
  try {
    lock->lock();
    flog->open();
    // Update flaglog and instance state
    for (vector <ServiceInstance*>::iterator i = instances.begin();
	 i!= instances.end(); i++ ) {
      Team* t = (*i)->getTeam();
      
      if((*i)->getStatus() == ServiceInstance::up) {
	FlagLogLine fl(t->getNum(), t->getNum(), num, roundNb - 1);
	if(flog->contains(fl)) {
	  LOG("Flaglog already contains service");
	}
	else {
	  flog->addLine(fl);
	}
      }
      (*i)->updateState(state);
    }
    
    // Update team score.
    if (roundNb > (1 + validityperiod)) {
      vector<Team*> teams = Globals::get()->getTeams();
      uint16_t scoreRound = roundNb - 1 - validityperiod;
      for (vector <ServiceInstance*>::iterator i = instances.begin();
	   i!= instances.end(); i++ ) {
	bool selfHacked = false;
	vector<uint8_t>  hackers;
	string hackerlist;
	Team* t = (*i)->getTeam();
	hackers = flog->getHackers(t->getNum(), num, scoreRound, selfHacked);
	if (selfHacked) {
	  if(hackers.size() == 0) {
	    LOG("SCORE: Defensive (" << t->getName() << "->" 
		<< t->getName() << "." << name << ") +" << defensivescore); 
	    t->addDefensiveScore(defensivescore);
	  }
	  else {
	    LOG("SCORE: Pitty (" << t->getName() << "->" 
		<< t->getName() << "." << name << ") +" << pittyscore); 
	    t->addDefensiveScore(pittyscore);
	  }
	}
	if (hackers.size()){
	  uint32_t points = offensivescore / hackers.size();
	  if(offensivescore % hackers.size()) points++;
	  for (vector<uint8_t>::iterator j = hackers.begin(); j!= hackers.end(); j++) {
	    if(*j > teams.size() || *j == 0) {
	      LOG("Error, hacked by unknown team (" << *j << ") (" << t->getName() << "." << name << ")" );
	    }
	    else {
	      Team* hackingTeam = teams[(*j)-1];
	      float upfrac = 1;
	      if (Globals::get()->getFractionmode()) {
		upfrac = ((float)hackingTeam->getServiceUpCount()) /  
		  ((float)Globals::get()->getServices().size());
	      }
	      uint32_t thispoints = (uint32_t)ceilf(upfrac * points);
	      char tmp[10];
	      tmp[9] = '\0';
	      snprintf(tmp, 9, "%hhu", *j);
	      if(hackerlist.size()) hackerlist.append(",");
	      hackerlist.append(tmp);
	      LOG("SCORE: Offensive (" << hackingTeam->getName() << "->" 
		  << t->getName() << "." << name << ") + " << points << "*" << upfrac << 
		  " (" << thispoints << ")");
	      hackingTeam->addOffensiveScore(thispoints);
	      
	      // Update the per-service - per-team score
	      for(vector <ServiceInstance*>::iterator i2 = instances.begin(); i2 != instances.end(); i2++) {
		if((*i2)->getTeam() == hackingTeam){
		  printf("Adding per service score\n");
		  (*i2)->addPerServiceScore(thispoints);
		  break;
		}
	      }
	    }	  
	  }
	}
	
	(*i)->setHackers(hackerlist);
	(*i)->updateState(state);
	t->updateState(state);
      }

      flog->purge(num, scoreRound + 1);
    }
    
    roundNb++;
    state->updateService(num, roundNb);    

    flog->save();
    state->save();
    lock->unlock();
  }
  catch (StateFileException e) {
    lock->unlock();
    LOG("Statefile error: " << e.toString());
  }
  catch (FlagLogException e) {
    lock->unlock();
    LOG("Flaglog error: " << e.toString());
  }
  catch (LockFileException e) {
    LOG("Lockfile error: " << e.toString());
  }
  
}

string Service::getFullScriptPath(const string& path) {
  if (path[0] == '/') return path;
  else return Globals::get()->getScriptdir() + path;
}

NetworkUsage::NetworkUsage(string script, float roundlength, float penalty){
  scriptfilename = getFullScriptPath(script);
  this->script = new AsyncScript(scriptfilename);
  this->roundlength = roundlength;
  this->penalty = penalty;
  running = false;
}

NetworkUsage::~NetworkUsage() {
  if(script) delete script;
}

void NetworkUsage::startScript(){
  try {
    script->run();
  } catch (AsyncScriptException e) {
    LOG("Error starting network usage script, exception:" << e.toString());
  } 
  running = true;
}

void NetworkUsage::scriptTimeout(){
  running = false;
  try {
    if(!script->stop()) {
      LOG("Network usage script timed out");
    }
    else if (!script->resultReady()) {
      LOG("Error, network usage script result not ready");
    }
    else if (script->getExitcode() != 0) {
      LOG("Error, network usage script returned exitcode: " << script->getExitcode());
      LOG("Network usage script said: " << script->getStdout());
   }
    else {
      vector<Team*> teams = Globals::get()->getTeams();

      // Everything is fine now, parse output of script.
      TRACE("Network usage script said: " << script->getStdout());
      vector<string> tokens = split(script->getStdout());
      for(vector<string>::size_type i=0; (i +3) < tokens.size(); i+=4) {
	string cidr = tokens[i];
	string count = tokens[i+1];
	char* tptr = NULL;
	uint32_t count_i = (uint32_t)strtoul(count.c_str(), &tptr, 10);
	if(!tptr || *tptr) {
	  LOG("Error parsing usage output, illegal int: " << count);
	}
	LOG("Usage Net: " << cidr << " count " << count_i << " factor " << penalty);
	for(vector<Team*>::iterator t=teams.begin(); t!= teams.end(); t++) {
	  if ((*t)->getCidr() == cidr) {
	    (*t)->setPenaltyScore((uint32_t)(((float)count_i) * penalty)); 
	  }
	}
      }
    }
  }
  catch (AsyncScriptException e) {
    LOG("Error stopping network usage script, exception:" << e.toString());
  }
}

bool NetworkUsage::isRunning() {
  return running;
}

float NetworkUsage::getRoundlength() {
  return roundlength;
}

bool NetworkUsage::validateScripts() {
  struct stat s;
  if (stat(scriptfilename.c_str(), &s) != 0) {
    cerr << "Cannot access script " << scriptfilename << endl;
    return false;
  }
  if (  (s.st_mode & S_IXOTH) == 0) {
    cerr << "Script " << scriptfilename << " is not executable" << endl;
    return false;
  }
    
  return true;
}

vector<string> NetworkUsage::split(const string& s) {
  vector<string> ret;
  string::size_type p1 = 0;
  string::size_type p2 = 0;

  while ((p2 = s.find_first_of(" \t\n\r", p1)) != string::npos) {
    ret.push_back(s.substr(p1, p2-p1));
    p1 = p2 + 1;
  }
  
  ret.push_back(s.substr(p1));

  
  return ret;
}

string NetworkUsage::getFullScriptPath(const string& path) {
  if (path[0] == '/') return path;
  else return Globals::get()->getScriptdir() + path;
}



