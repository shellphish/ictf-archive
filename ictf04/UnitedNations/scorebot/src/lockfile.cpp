#include "lockfile.hpp"

#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/stat.h>

#define RETRY_USECS 1000 // Retry every millisec
#define HOSTNAME_LEN 50

LockFile::LockFile(const string& filename) {
  char tmp[HOSTNAME_LEN+1];
  tmp[HOSTNAME_LEN] = 0;
  pid_t mypid = getpid();

  is_locked = false;
  lockfile = filename;
  gethostname(tmp, HOSTNAME_LEN);
  privateLockfile = lockfile + "." + tmp + ".";
  snprintf(tmp, HOSTNAME_LEN, "%lu", (unsigned long)mypid);
  privateLockfile.append(tmp);

  deleteFile();
  createFile();
}

LockFile::~LockFile() {
  try {
    destroy();
  }
  catch (LockFileException e) {
    fprintf(stderr, "Destructor %s\n", e.toString().c_str());
  }
}

void LockFile::createFile() {
  int fd;
  if((fd = open(privateLockfile.c_str(), O_CREAT | O_EXCL)) == -1) {
    throw LockFileException("Could not open private lockfile: ").
      append(privateLockfile).append(" ").append(strerror(errno));
  }
  close(fd);
}

void LockFile::deleteFile() {
  int err = unlink(privateLockfile.c_str());
  if(err == -1 && errno != ENOENT) {
    throw LockFileException("Could not delete private lockfile: ").
      append(privateLockfile).append(" ").append(strerror(errno));
  }
}


bool LockFile::lock(uint32_t timeout_msecs) {
  struct timeval now;
  struct timeval endtime;

  if(timeout_msecs) {
    gettimeofday(&endtime, NULL);
    endtime.tv_sec += timeout_msecs / 1000;
    endtime.tv_usec +=  timeout_msecs % 1000;
    if(endtime.tv_usec > 1000000) {
      endtime.tv_usec -= 1000000;
      endtime.tv_sec++;
    }
  }
  
  while (!tryLock()) {
    if(timeout_msecs) {
      gettimeofday(&now, NULL);
      if (timercmp(&now, &endtime, >=)) return false;
    }
    usleep(RETRY_USECS);
  }
  return true;
}


// This algorithm is from man open(2)
bool LockFile::tryLock() {
  if(is_locked) return true;
  is_locked = true;
  struct stat buf;
  int ret = link(privateLockfile.c_str(), lockfile.c_str());
  if(ret == 0) return true;
  
  ret = stat(privateLockfile.c_str(), &buf);
  if(ret != 0) {
    throw LockFileException("Could not stat file ").
      append(privateLockfile).append(" :").append(strerror(errno));
  }
  
  if(buf.st_nlink == 2) return true;

  is_locked = false;
  return false;
}

bool LockFile::unlock() {
  if(!is_locked) return true;
 
  int err = unlink(lockfile.c_str());
  if(err == -1 && errno != ENOENT) {
    throw LockFileException("Could not delete lockfile: ").
      append(lockfile).append(" ").append(strerror(errno));
  }
  is_locked = false;
  return true;
}

void LockFile::destroy() {
  unlock();
  deleteFile();
}
