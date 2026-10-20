#!/usr/bin/python

import sys
import telnetlib
import time
import hashlib

class SetFlag():
    def execute(self, ip, port, flag):
        tn = telnetlib.Telnet(ip, port=port, timeout=5)

        tn.write("toilet flush '" + flag + "'\n")
        sys.stdout.flush()
        m = tn.read_until("!!!")

        self.flag_id = m[-9:-3]
        self.token = hashlib.md5(flag).hexdigest()

        self.error = 0
        self.error_msg = ""

    def result(self):
        return {
            'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
        }
