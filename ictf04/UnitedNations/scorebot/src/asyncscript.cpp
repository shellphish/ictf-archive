#include "asyncscript.hpp"

#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define READ_BUF_SIZE 100

void AsyncScript::run() {
  pid_t pid;
  const char** argv = NULL;
  int carg =  0;
  int pipes[2];
  
  if(running) throw AsyncScriptException("Script is already running");
  
  ready = false;
  
  if(pipe(pipes) == -1) {
    throw AsyncScriptException("Error creating pipe");
    return;
  }
  
  switch ((pid = fork())) {
  case -1:
    throw AsyncScriptException("Error forking");
    return;
  case 0:
    //  Child, execute script.
    close(pipes[0]);
    dup2(pipes[1], STDOUT_FILENO);
    argv = new const char*[params.size() + 2];
    argv[0] = script.c_str();
    carg = 1;
    for( vector<string>::const_iterator i = params.begin(); i!= params.end(); i++) {
      argv[carg] = (*i).c_str();
      carg++;
    }
    argv[carg] = NULL;
    
    execv(script.c_str(), (char**)argv);
    // No need to delete args,. we are already in child.
    perror("Exec failed");
    // Should never get here.
    exit(-1);
  default:
    // Parent
    close(pipes[1]);
    running = true;
    scriptPID = pid;
    scriptPipe = pipes[0];
  }
}

bool AsyncScript::stop() {
  int status;
  if(!running) throw AsyncScriptException("Script is not running");
  running = false;
  stdoutstr = "";

  int ret = waitpid(scriptPID, &status, WNOHANG);
  // Check if script has exited.
  if(ret <= 0) {
    // Script is still running, send SIGTERM
    kill(scriptPID, SIGTERM);
    // Reap child -- this might hang if script does not exit on sigterm
    waitpid(scriptPID, &status, 0);
    close(scriptPipe);
    return false;
  }
  
  if( WIFEXITED(status) ) {
    exitcode = WEXITSTATUS(status);
    char tmp[READ_BUF_SIZE];
    int len;
    fcntl(scriptPipe, F_SETFL, O_NONBLOCK);
    while ( (len = read(scriptPipe, tmp, READ_BUF_SIZE - 1)) > 0) {
      tmp[len] = 0;
      stdoutstr += tmp;
      if (len != READ_BUF_SIZE - 1) break;
    }
    close(scriptPipe);
    ready = true;
  }
  else {
    close(scriptPipe);
    return false;
  }
  
  return true;
}

bool AsyncScript::resultReady() {
  return ready;
}

string AsyncScript::getStdout() {
  if (!ready) throw AsyncScriptException("Result not ready");
  return stdoutstr;
}

int AsyncScript::getExitcode() {
  if (!ready) throw AsyncScriptException("Result not ready");
  return exitcode;
}
