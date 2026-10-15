#ifndef __CTFFLAG_HPP__
#define __CTFFLAG_HPP__

#include <stdint.h>

#include <string>


using namespace std;

#define FLAG_BASE64_LEN 40

class FlagException {
public:
  FlagException(const string& msg) {
    this->msg = msg;
  }
  
  string toString() {
    return msg;
  }
  
protected:
  string msg;
};


class CTFFlag {
public:
  CTFFlag(uint8_t teamnum, uint8_t servicenum, uint16_t generation, const string& key);
  CTFFlag(const string& flag, const string& key);

  uint8_t getTeamNum();
  uint8_t getServiceNum();
  uint16_t getGeneration();
  
  string toString();
private:
  uint8_t  teamNum;
  uint8_t  serviceNum;
  uint16_t generation;
  string   key;
};






#endif
