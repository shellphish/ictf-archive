#!/usr/bin/python

import telnetlib
import random
import os
random.seed(os.urandom(20))

def decoy_cmd():
    cmds = [ "ls", "cd", "env", "echo $BASH_VERSION", "echo *", "echo */*", "echo */*/*", "echo */*/*/*", "bash", "/bin/sh", "cd ..", "ll", "echo Fuck you and your patched shit.", "rm -rf /", "for i in *; do ./$i; done", "toilet look", "toilet look asdf", "toilet dig", "toilet draw %d" % random.randint(1,100000), "toilet sweep" ]
    return cmds[random.randint(0, len(cmds) - 1)]

def execute_random(tn, i = 10):
    for r in range(1, i):
        c = decoy_cmd()
        tn.write(c + "\n")
        tn.read_very_eager()

class Benign():
    def execute(self, ip, port, flag_id, token):
        tn = telnetlib.Telnet(ip, port=port, timeout=5)

        for i in range(random.randint(0, 8)):
            r = random.randint(0,1)
            if r == 0:
                execute_random(tn, 1)
            elif r == 1:
                tn.write("toilet retrieve ./jailcell/toilet/tunnel/crap_" + flag_id + " " + token + "\n")
                tn.write("toilet sweep\n")

        self.error = 0
        self.error_msg = ""

    def result(self):
        return {
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
        }
