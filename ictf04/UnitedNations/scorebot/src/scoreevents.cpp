#include "eventprocessor.hpp"
#include "networkobjects.hpp"
#include "lockfile.hpp"
#include "statefile.hpp"

static void updateTeamStates() {
  vector<Team*> teams = Globals::get()->getTeams();
  StateFile* state = Globals::get()->getStatefile();
  LockFile* lock = Globals::get()->getLockfile();
  
  for(vector<Team*>::iterator i = teams.begin(); i!=teams.end(); i++) {
    (*i)->updateState(state);
  }
  try {
    lock->lock();
    state->save();
    lock->unlock();
  }
  catch (StateFileException e) {
    lock->unlock();
    LOG("Statefile error (eventprocessor): " << e.toString());
  }
  catch (LockFileException e) {
    LOG("Lockfile error (eventprocessor): " << e.toString());
  }
}

static uint32_t getrand(uint32_t min, uint32_t max) {
  return min+(uint32_t) ((1.0*max) * rand() / (RAND_MAX+1.0));
}

class ProbeEvent : public Event {
public:
  ProbeEvent (const struct timeval& now, uint32_t msecdelay, ServiceInstance* si) : Event(now, msecdelay) {
    this->instance = si;
  }
  
  void process(EventProcessor* processor) {
    instance->startScore();
  }
  
  ServiceInstance* instance;
};

class ProbeTimeoutEvent : public Event {
public:
  ProbeTimeoutEvent (const struct timeval& now, uint32_t msecdelay, ServiceInstance* si) : Event(now, msecdelay) {
    this->instance = si;
  }
  
  void process(EventProcessor* processor) {
    instance->scoreTimeout();
  }
  
  ServiceInstance* instance;
};



class RoundEvent : public Event {
public:
  RoundEvent (const struct timeval& now, uint32_t msecdelay, Service* s) : Event(now, msecdelay) {
    this->service = s;
  }

  void process(EventProcessor* processor) {
    if(!service->initial) {
      LOG("Scoring round " << service->getRoundNb() << " for service " << service->getName());
      service->endOfRound();
    }
    else {
      service->initial = false;
    }
    
    if(Globals::get()->getTerminate())  return;
   
    struct timeval now;
    gettimeofday(&now, NULL);

    uint32_t maxtime = (uint32_t)((service->getRoundlength() - service->getScriptTO()) * 1000) - 1;
    uint32_t timeout = (uint32_t)(service->getScriptTO() * 1000);
    
    const vector<ServiceInstance*> instances = service->getServiceInstances();
    for(vector<ServiceInstance*>::const_iterator i = instances.begin();
	i!= instances.end(); i++) {
      //printf("Adding instance %s\n", (*i)->getTeam()->getName().c_str());
      uint32_t time = getrand(0, maxtime);
      processor->addEvent(new ProbeEvent(now,time, *i));
      processor->addEvent(new ProbeTimeoutEvent(now,time + timeout , *i));
    }
    
    processor->addEvent(new RoundEvent(now,(uint32_t)(service->getRoundlength() * 1000), service));
    LOG("Starting round " << service->getRoundNb() << " for service " << service->getName());
  }

  Service* service;
};

class PenaltyEvent : public Event {
  public:
  PenaltyEvent (const struct timeval& now, uint32_t msecdelay, NetworkUsage* u) : Event(now, msecdelay) {
    this->usage = u;
  }
  
  void process(EventProcessor* processor) {
    if(usage->isRunning()) {
      LOG("Updating penalty score");
      usage->scriptTimeout();
      updateTeamStates();
    }
    
    if(Globals::get()->getTerminate())  return;
    
    struct timeval now;
    gettimeofday(&now, NULL);
    processor->addEvent(new PenaltyEvent(now, (uint32_t)(usage->getRoundlength() * 1000), usage));
    
    usage->startScript();
  }
  
  NetworkUsage* usage;
};

class TrendScoreEvent : public Event {
public:
  TrendScoreEvent (const struct timeval& now, uint32_t msecdelay) : Event(now, msecdelay) {
  }
  
  void process(EventProcessor* processor) {
    LOG("Updating trend score");
    vector<Team*> teams = Globals::get()->getTeams();
    for(vector<Team*>::iterator i=teams.begin(); i!= teams.end(); i++) {
      (*i)->decay();
    }
    updateTeamStates();

    if(Globals::get()->getTerminate())  return;
    struct timeval now;
    gettimeofday(&now, NULL);
    processor->addEvent(new TrendScoreEvent(now, (uint32_t)(Globals::get()->getDecaytime() * 1000)));
  }
};


void do_process(vector<Service*> services, NetworkUsage* usage) {
  EventProcessor p;
  struct timeval now;
  gettimeofday(&now, NULL);
  for(vector<Service*>::iterator i = services.begin(); i != services.end(); i++) {
    p.addEvent(new RoundEvent(now, 0, *i));
  }
  if(usage) p.addEvent(new PenaltyEvent(now, 0, usage));
  p.addEvent(new TrendScoreEvent(now, 0));
  p.run();
}
