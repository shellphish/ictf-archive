#include "flaglog.hpp"
#include "tokenizer.hpp"

#include <unistd.h>

#include <fstream>
#include <iostream>

FlagLog::FlagLog(const string& filename, bool init) {
  this->filename = filename;
  if(init) {
    ofstream out(filename.c_str());
    if (!out.good()) {
      throw FlagLogException("Could not create flaglog: ").append(filename);
    }
    out.close();
  }
}
void FlagLog::open() {
  lines.clear();
  ifstream in(filename.c_str());
  if (!in.good()) {
    throw FlagLogException("Could not open flaglog: ").append(filename);
  }

  Tokenizer tok(&in);
  while (tok.eat()) {
    unsigned long hacking_teamnum;
    unsigned long victim_teamnum;
    unsigned long servicenum;
    unsigned long generation;
    char* tptr;
    
    string token = tok.getToken();
    hacking_teamnum = strtoul(token.c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') throw FlagLogException("Illegal integer in flaglog");
    if(hacking_teamnum > 255) throw FlagLogException("Integer out of range in flaglog");

    if(!tok.eat()) throw FlagLogException("Premature EOF in flaglog");
    victim_teamnum = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') throw FlagLogException("Illegal integer in flaglog");
    if(victim_teamnum > 255) throw FlagLogException("Integer out of range in flaglog");

    if(!tok.eat()) throw FlagLogException("Premature EOF in flaglog");
    servicenum = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') throw FlagLogException("Illegal integer in flaglog");
    if(servicenum > 255) throw FlagLogException("Integer out of range in flaglog");

    if(!tok.eat()) throw FlagLogException("Premature EOF in flaglog");
    generation = strtoul(tok.getToken().c_str(), &tptr, 10);
    if(!tptr || *tptr != '\0') throw FlagLogException("Illegal integer in flaglog");
    if(generation > 65535) throw FlagLogException("Integer out of range in flaglog");

    if(!tok.eat()) throw FlagLogException("Premature EOF in flaglog");
    if(tok.getToken() != ";") throw FlagLogException("Expected ';' in flaglog");
 
    FlagLogLine line((uint8_t)hacking_teamnum, (uint8_t) victim_teamnum, 
		     (uint8_t) servicenum, (uint16_t) generation);

    addLine(line);
  }

}

bool FlagLog::contains(const FlagLogLine& line) {
  for(vector<FlagLogLine>::iterator i = lines.begin(); i!=lines.end(); i++) {
    if(line == (*i)) return true;
  }
  return false;
}

void FlagLog::addLine(const FlagLogLine& line) {  
  lines.push_back(line);
}

vector<uint8_t> FlagLog::getHackers(uint8_t victim_teamnum, uint8_t servicenum, uint16_t generation, bool& retSelfHacked) {
  vector<uint8_t> ret;
  retSelfHacked = false;

  for(vector<FlagLogLine>::iterator i = lines.begin(); i!=lines.end(); i++) {
    if((*i).victim_teamnum == victim_teamnum &&
       (*i).servicenum == servicenum &&
       (*i).generation == generation) {
      if((*i).hacking_teamnum == victim_teamnum) {
	retSelfHacked = true;
      }
      else {
	ret.push_back((*i).hacking_teamnum);
      }
    }
  }
  
  return ret;
}

void FlagLog::purge(uint8_t servicenum, uint16_t generation) {
  vector<FlagLogLine>::size_type i = 0;
  while(i < lines.size()) {
    if(lines[i].servicenum == servicenum && lines[i].generation < generation) {
      lines.erase(lines.begin() + i);
    }
    else {
      i++;
    }
  }
}


void FlagLog::save() {
  ofstream out(filename.c_str());
  if (!out.good()) {
    throw FlagLogException("Could not open flaglog for writing: ").append(filename);
  }
  
  for(vector<FlagLogLine>::iterator i = lines.begin(); i!=lines.end(); i++) {
    out << (uint16_t)(*i).hacking_teamnum << " " << 
      (uint16_t)(*i).victim_teamnum << " " << 
      (uint16_t)(*i).servicenum << " " << (*i).generation << ";\n"; 
  }
  out.close();
}

