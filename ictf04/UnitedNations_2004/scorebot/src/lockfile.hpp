#ifndef __LOCKFILE_HPP__
#define __LOCKFILE_HPP__

#include <stdint.h>

#include <string>
using namespace std;

class LockFileException {
  public:
  LockFileException(const string& msg) {
    this->msg = msg;
  }
  
  string toString() {
    return msg;
  }
  
  LockFileException append(const string& msg) {
    this->msg.append(msg);
    return *this;
  }

protected:
  string msg;

};

class LockFile {
public:
  LockFile(const string& filename);
  ~LockFile();
  bool lock(uint32_t timeout_msecs = 0); // 0 is inifinate
  bool tryLock();
  bool unlock();
  void destroy();

private:
  void createFile();
  void deleteFile();
  bool is_locked;
  string lockfile;
  string privateLockfile;
};

#endif
