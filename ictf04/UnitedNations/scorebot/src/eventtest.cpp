#include <stdio.h>

#include "eventprocessor.hpp"

class TestEvent : public Event {
public:
  TestEvent(const struct timeval& time, int no) : Event(time) {n = no;}
  TestEvent (uint32_t msecdelay, int no) : Event(msecdelay) {n = no;}

  void process(EventProcessor* processor) {
    printf("Processed event %i, %lu.%lu\n", n, time.tv_sec, time.tv_usec);
  }
  int n;
};

int main(int argc, char** argv) {
  EventProcessor p;
  p.addEvent(new TestEvent(0,1));
  p.addEvent(new TestEvent(0,2));
  p.addEvent(new TestEvent(0,3));
  p.addEvent(new TestEvent(20000,4));
  p.addEvent(new TestEvent(10000,5));
  p.addEvent(new TestEvent(1000,6));
  p.addEvent(new TestEvent(2000,7));
  p.addEvent(new TestEvent(0,8));
  
  p.run();


  return 0;
}
