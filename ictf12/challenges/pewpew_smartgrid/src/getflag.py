#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GetFlag():
    error = -1
    token = None
    flag = None
    err_msg = ""

    def execute(self, ip, port, flag_id=None, token=None):
        import random
        import socket
        import time
        import re

        self.flag = None

        sock = socket.socket()
        sock.settimeout(20)

        self.error = -1
        self.err_msg = "Timeout"
        try:
            sock.connect((ip, port))
        except:
            return

        sock.recv(16384)
        sock.send("login {} {}\n".format(flag_id, token))
        r = sock.recv(16384)
        if "successfully" not in r:
            self.err_msg = "Flag and Token not available anymore"
            self.error = 1

        sock.recv(16384)
        data, lines = "", []
        if random.randint(0, 0) == 1:
            # This mode is bugged right now
            for i in xrange(0, random.randint(19, 25)):
                sock.send("review {}\n".format(i))
                ls = []
                while not "~> " in ls:
                    data += sock.recv(4096)
                    ls = data.split("\n")
                lines.extend(ls)
        else:
            sock.settimeout(1)
            try:
                sock.recv(4096)
            except:
                pass

            sock.send("review\n")
            while not "~> " in lines:
                data += sock.recv(4096)
                lines = data.split("\n")
        flag = ""

        time.sleep(0.25)

        rgx = re.compile("ACC=\d+: \d+ (?P<val>\d+)")
        matches = []
        for d in lines:
            m = rgx.search(d)
            if m:
                matches.append(m.group("val"))

        for m in matches:
            value = int(m, 10)
            value = "%08x" % value
            flag += "{}{}{}{}".format(chr(int(value[0:2], 16)),
                                      chr(int(value[2:4], 16)),
                                      chr(int(value[4:6], 16)),
                                      chr(int(value[6:8], 16)))

        flag = flag[:64]
        print "*] Flag: flag_id={} flag={} token={}".format(flag_id, flag, token)

        sock.send("exit\n")
        sock.close()

        self.err_msg = ""
        self.error = 0
        self.token = token
        self.flag = flag

    def result(self):
        return {'FLAG': self.flag,
                'ERROR': self.error,
                "ERROR_MSG" : self.err_msg,
                "COOKIE": self.token}

if __name__ == "__main__":
    e = GetFlag()
    import sys
    e.execute(sys.argv[1], 14389, sys.argv[2], sys.argv[3])
    print e.result()
