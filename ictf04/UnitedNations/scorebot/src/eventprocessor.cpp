#include "eventprocessor.hpp"

EventProcessor::EventProcessor(){
}

void EventProcessor::addEvent(Event* e){
  queue.push(e);
}

void EventProcessor::run(){
  Event* nextEvent = NULL;

  while (!queue.empty()) {
    nextEvent = queue.top();
    queue.pop();
    sleepUntil(nextEvent->time);
    nextEvent->process(this);
    delete nextEvent;
  }
}

void EventProcessor::sleepUntil(const struct timeval& until) {
  struct timeval now;
  gettimeofday(&now, NULL);
  if (timercmp(&until, &now, <) || timercmp(&until, &now, ==)) return;
  
  struct timeval period;
  timersub(&until, &now, &period);
  if(period.tv_sec) {
    //printf("Sleeping %lu seconds\n", period.tv_sec);
    sleep(period.tv_sec);
  }
  else if (period.tv_usec) {
    //printf("Sleeping %lu useconds\n", period.tv_usec);
    usleep(period.tv_usec);
  }
  sleepUntil(until);
}
