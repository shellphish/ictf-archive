#ifndef __EVENTPROCESSOR_HPP__
#define __EVENTPROCESSOR_HPP__

#include <sys/time.h>
#include <stdint.h>

#include <vector>
#include <queue>
using namespace std;

class EventProcessor;

class Event {
public:
  Event(const struct timeval& time) {
    this->time = time;
  }
  Event(uint32_t msecdelay) {
    struct timeval now;
    gettimeofday(&now, NULL);
    
    struct timeval delay;
    delay.tv_sec = msecdelay / 1000;
    delay.tv_usec = (msecdelay %1000) * 1000;

    timeradd(&now, &delay, &time);
  }
  
  Event(const struct timeval& now, uint32_t msecdelay) {
    struct timeval delay;
    delay.tv_sec = msecdelay / 1000;
    delay.tv_usec = (msecdelay %1000) * 1000;
    
    timeradd(&now, &delay, &time);
  }
  
  virtual ~Event(){}
  virtual void process(EventProcessor* processor) = 0x0;
  struct timeval time;
};

struct eventcmp : public binary_function<Event*, Event*,bool>
{
  bool operator()(const Event* __x, const Event* __y) const 
  { return timercmp(&(__x->time),  &(__y->time), >); }
};


typedef priority_queue<Event*, vector<Event*>, eventcmp > EventQueue;

class EventProcessor {
public:
  EventProcessor();
  void addEvent(Event* e);
  void run();
private:
  void sleepUntil(const struct timeval& until);
  EventQueue queue; 
};










#endif
