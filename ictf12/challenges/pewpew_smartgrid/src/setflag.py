#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
import socket
import time
from datetime import datetime

class SetFlag():
    error = -1
    token = None
    flag_id = None
    flag = None
    err_msg = ""

    def execute(self, ip, port, flag=None):
        tstart = datetime.now()

        flag_id = "".join(random.choice(string.ascii_letters + string.digits) for x in range(random.randint(16,32)))

        if flag is None:
            flag = "FLG" + "".join(random.choice(string.ascii_letters + string.digits) for x in range(61))

        token = "".join(random.choice(string.ascii_letters + string.digits) for x in range(random.randint(16,32)))

        self.error = -1
        self.err_msg = "Timeout on connect: {}".format(datetime.now() - tstart)
        sock = socket.socket()

        sock.connect((ip, port))
        self.err_msg = "Timeout after connect"
        sock.recv(4096)

        sock.send("register {}\n".format(flag_id))
        self.err_msg = "Timeout after register {} {} {}".format(ip, port, datetime.now() - tstart)

        print "*] Flag: flag_id={} flag={} token={}".format(flag_id, flag, token)

        for i in xrange(0, len(flag), 4):
            in_hex = "%02x%02x%02x%02x" % (ord(flag[i]), ord(flag[i+1]),
                                           ord(flag[i+2]), ord(flag[i+3]))
            in_int = int(in_hex, 16)
            sock.recv(4096)
            sock.send("report {}\n".format(in_int))
        self.err_msg = "Timeout after report flag {} {} {}".format(ip, port, datetime.now() - tstart)

        for i in range(random.randint(0, 100-16)):
            sock.recv(4096)
            sock.send("report {}\n".format(random.randint(0, 2**31)))
        self.err_msg = "Timeout after random garbage {} {} {}".format(ip, port, datetime.now() - tstart)


        #self.err_msg = "Timeout after report random garbage {} {} {}".format(ip, port, datetime.now() - tstart)

        #sock.recv(4096)
        sock.send("store {}\n".format(token))
        self.err_msg = "Timeout after store {} {} {}".format(ip, port, datetime.now() - tstart)
        sock.recv(4096)

        if random.randint(0, 1) == 1:
            sock.send("review\n")
            sock.recv(4096)
        sock.close()

        self.error = 0
        self.err_msg = ""
        self.token = token
        self.flag = flag
        self.flag_id = flag_id

    def result(self):
        return {'FLAG': self.flag,
                'FLAG_ID': self.flag_id,
                'ERROR': self.error,
                "ERROR_MSG": self.err_msg,
                "COOKIE": self.token}


if __name__ == "__main__":
    e = SetFlag()
    import sys
    e.execute(sys.argv[1], 14389)
    print e.result()
