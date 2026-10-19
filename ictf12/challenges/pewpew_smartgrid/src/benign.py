#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
import socket
import time


class Benign():
    error = -1
    data = None
    user = None
    token = None
    err_msg = ""

    def execute(self, ip, port, user=None, token=None):
        if user is None:
            user = "".join(random.choice(string.ascii_letters + string.digits) for x in range(random.randint(16,32)))

        data = "FLG" + "".join(random.choice(string.ascii_letters + string.digits) for x in range(61))

        self.data = data
        self.error = -1
        self.err_msg = "Timeout before connect"
        sock = socket.socket()
        sock.connect((ip, port))
        self.err_msg = "Timeout after connect"
        sock.recv(4096)

        if token is None:
            token = "".join(random.choice(string.ascii_letters + string.digits) for x in range(random.randint(16,32)))
            sock.send("register {}\n".format(user))
            self.err_msg = "Timeout after register"
        else:
            sock.send("login {} {}\n".format(user, token))
            resp = sock.recv(4 + len("Successfully identified."))
            if not "Successfully identified." in resp:
                self.error = 1
                return
            self.err_msg = "Timeout after login"

        print "*] Flag: flag_id={} flag={} token={}".format(user, data, token)

        for i in xrange(0, len(data), 4):
            in_hex = "%02x%02x%02x%02x" % (ord(data[i]), ord(data[i+1]),
                                           ord(data[i+2]), ord(data[i+3]))
            in_int = int(in_hex, 16)
            sock.recv(16384)
            sock.send("report {}\n".format(in_int))
        self.err_msg = "Timeout after report pseudo flag"

        for i in range(random.randint(0, 200-16)):
            sock.recv(16384)
            sock.send("report {}\n".format(random.randint(0, 2**31)))
        self.err_msg = "Timeout after report garbage"

        # verify that values were written properly

        sock.send("store {}\n".format(token))
        self.err_msg = "Timeout after store"
        sock.recv(16384)

        sock.close()

        # try to login
        # purge user

        self.token = token
        self.user = user
        self.error = 0
        self.err_msg = "First part done properly, not cleaned up though"

        timeout = random.randint(1, 8)
        print "Sleeping... {}".format(timeout)

        time.sleep(timeout)

        self._purge(ip, port)

    def _purge(self, ip, port):
        if self.user is None or self.token is None:
            return

        self.error = -1
        sock = socket.socket()
        sock.connect((ip, port))
        self.err_msg = "Timeout after purge connect"

        sock.recv(16384)
        sock.send("login {} {}\n".format(self.user, self.token))
        resp = sock.recv(16384)
        self.err_msg = "Timeout after login"
        if not "Successfully identified." in resp:
            self.error = 1
            return

        sock.recv(16384)
        sock.send("purge\n")
        sock.recv(16384)
        self.err_msg = "Timeout after purge"

        sock.close()
        self.error = 0
        self.err_msg = "Successful for {} {}".format(ip, port)

    def result(self):
        return {'ERROR': self.error, 'ERROR_MSG' : self.err_msg}


if __name__ == "__main__":
    e = Benign()
    import sys
    e.execute(sys.argv[1], 14389)
