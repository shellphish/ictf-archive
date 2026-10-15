#ifndef __FLAGLOG_HPP__
#define __FLAGLOG_HPP__

#include <stdint.h>

#include <vector>
#include <string>
using namespace std;

class FlagLogException {
public:
  FlagLogException(const string& msg) {
    this->msg = msg;
  }
  
  string toString() {
    return msg;
  }
  
  FlagLogException append(const string& msg) {
    this->msg.append(msg);
    return *this;
  }

protected:
  string msg;
};

class FlagLogLine {
public:
  FlagLogLine(uint8_t hacking_teamnum, uint8_t victim_teamnum, uint8_t servicenum, uint16_t generation) {
    this->hacking_teamnum = hacking_teamnum;
    this->victim_teamnum = victim_teamnum;
    this->servicenum = servicenum;
    this->generation = generation;
  }

  bool operator==(const FlagLogLine& right) const {
    if(hacking_teamnum == right.hacking_teamnum &&
       victim_teamnum == right.victim_teamnum &&
       servicenum == right.servicenum &&
       generation == right.generation) {
      return true;
    }
    else {
      return false;
    }
  }

  uint8_t hacking_teamnum;
  uint8_t victim_teamnum;
  uint8_t servicenum;
  uint16_t generation;
};

class FlagLog {
public:
  FlagLog(const string& filename, bool init = false);
  
  void open();
  bool contains(const FlagLogLine& line);
  void addLine(const FlagLogLine& line);
  vector<uint8_t> getHackers(uint8_t victim_teamnum, uint8_t servicenum, uint16_t generation, bool& retSelfHacked);
  void purge(uint8_t servicenum, uint16_t generation);
  void save();

protected:

  string filename;
  vector<FlagLogLine> lines;
};

#endif
