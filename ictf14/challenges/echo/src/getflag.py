#!/usr/bin/env python

import socket
import random
import sys
import string

HOST, PORT = "0.0.0.0", 9148

def recv_all(s, n):
    ret = ""
    while len(ret) < n:
        c = s.recv(1)
        if len(c) == 0:
            break
        ret += c
    return ret

def recv_until(s, unt):
    ret = ""
    while True:
        c = s.recv(1)
        if len(c) == 0:
            break
        ret += c
        if c == unt:
            break
    return ret

class GetFlag(object):
    def __init__(self):
        self.r = { 'FLAG': '',
                    'ERROR': 42,
                    'ERROR_MSG': 'execute() haven\'t been called.'
                 }

    def _random_str(self, n=8):
        return "".join([ random.choice(string.uppercase + string.digits) for i in xrange(n) ])

    def execute(self, ip, port, flag_id, token):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))

        s.send('r') # Read the flag
        s.send(flag_id + token)

        flag = recv_until(s, '\n').strip('\n')

        self.r = { 'FLAG': flag,
                    'ERROR': 0,
                    'ERROR_MSG': ''
                 }

    def result(self):
        return self.r

def main():
    assert len(sys.argv) == 4
    ip = sys.argv[1]
    port = PORT # This is the normal port
    flag_id = sys.argv[2]
    token = sys.argv[3]

    getflag = GetFlag()
    getflag.execute(ip, port, flag_id, token)

    print getflag.result()

if __name__ == "__main__":
    main()

