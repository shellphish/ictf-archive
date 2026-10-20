#!/usr/bin/python

import telnetlib

class GetFlag():
    def execute(self, ip, port, flag_id, token, tn=None):
        tn = telnetlib.Telnet(ip, port=port, timeout=5) if tn is None else tn

        tn.write("toilet retrieve ./jailcell/toilet/tunnel/crap_" + flag_id + " " + token + "\n")
        tn.read_until(": ")
        self.flag = tn.read_until("\n")[:-1]

        tn.write("toilet sweep")
        self.error = 0
        self.error_msg = ""

    def result(self):
        return {
            'FLAG' : self.flag,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
        }
