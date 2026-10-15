#ifndef __ASYNCSCRIPT_HPP__
#define __ASYNCSCRIPT_HPP__

#include "util.hpp"

class AsyncScriptException {
  public:
  AsyncScriptException(const string& msg) {
    this->msg = msg;
  }
  
  string toString() {
    return msg;
  }
  
  AsyncScriptException append(const string& msg) {
    this->msg.append(msg);
    return *this;
  }

protected:
  string msg;
};

class AsyncScript {
public:
  AsyncScript(const string& script) {
    this->script = script;
    running = false;
    ready = false;
  }
  AsyncScript(const string& script, const vector<string>& params) {
    this->script = script;
    this->params = params;
    running = false;
    ready = false;
  }
  void run();
  bool stop();
  bool resultReady();
  string getStdout();
  int getExitcode();
  
private:
  string script;
  vector<string> params;
  bool running;
  bool ready;
  pid_t scriptPID;
  int   scriptPipe;
  int exitcode;
  string stdoutstr;
};



#endif
