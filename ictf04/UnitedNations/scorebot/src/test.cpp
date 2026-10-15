#include <iostream>

#include "CTFFlag.hpp"
#include "asyncscript.hpp"
#include "tokenizer.hpp"

#define KEY "Supersecret"


vector<string> split(const string& s) {
  vector<string> ret;
  string::size_type p1 = 0;
  string::size_type p2 = 0;

  while ((p2 = s.find_first_of(" \t\n\r", p1)) != string::npos) {
    cerr << "Next '" << s.substr(p1, p2-p1) <<"'\n";
    ret.push_back(s.substr(p1, p2-p1));
    p1 = p2 + 1;
  }
   cerr << "Last '" << s.substr(p1) <<"'\n";
  ret.push_back(s.substr(p1));
  
  return ret;
}


static uint32_t getrand(uint32_t min, uint32_t max) {
  return min+(uint32_t) ((1.0*max) * rand() / (RAND_MAX+1.0));
}


int main (int argc, char** argv) {
  cerr << Tokenizer::quoteString("\\007") << endl;
  cerr << Tokenizer::quoteString("\\") << endl;
  cerr << Tokenizer::quoteString("007\\") << endl;
  cerr << Tokenizer::quoteString("\"007") << endl;
  cerr << Tokenizer::quoteString("\"") << endl;
  cerr << Tokenizer::quoteString("007\"") << endl;
  cerr << Tokenizer::quoteString("0\"07") << endl;
  cerr << Tokenizer::quoteString("00\\0") << endl;
  cerr << Tokenizer::quoteString("00\"0000") << endl;
  cerr << Tokenizer::quoteString("ABC") << endl;

  split("blah blah 1 2\n112121 1221212\tkjlkj");

  vector <int> test;
  test.push_back(1);
  test.push_back(2);
  test.push_back(3);
  test.push_back(4);
  test.push_back(5);
  test.push_back(6);
  test.push_back(7);

  vector<int>::size_type i = 0;

  while (i < test.size()) {
    printf("Processing %i\n", test[i]);
    if(test[i] == 1) {
      test.erase(test.begin() + i);
    }
    else {
      i++;
    }
  }

  for(vector<int>::iterator i = test.begin(); i!= test.end(); i++) {
    printf("%i\n", *i);
  }
  

  vector<string> args;
  args.push_back("arg1");
  args.push_back("arg2");
  
  AsyncScript script("./testscript", args);
  script.run();
  sleep(3);
  script.stop();
  if(script.resultReady()) {
    printf("Script exited: %i: %s\n", script.getExitcode(),
	   script.getStdout().c_str());
  }


  try {
    CTFFlag flag(1,2,1000, KEY);
    string flagval = flag.toString();
    printf("The flag is: %s\n", flagval.c_str());
    CTFFlag* flag2 = new CTFFlag(flagval, KEY  );
    printf("Flag is: %hhu %hhu %hu\n", flag2->getTeamNum(),
	   flag2->getServiceNum(), flag2->getGeneration());
  }
  catch (FlagException e) {
    printf("Exception: %s\n", e.toString().c_str());
  }
  return 0;
}
