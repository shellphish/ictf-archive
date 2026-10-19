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

class Benign(object):
    def __init__(self):
        self.r = { 'FLAG_ID': '',
                    'TOKEN': '',
                    'ERROR': 42,
                    'ERROR_MSG': 'execute() haven\'t been called.'
                 }

    def _random_str(self, n=8):
        return "".join([ random.choice(string.uppercase + string.digits) for i in xrange(n) ])

    def execute(self, ip, port, flag_id, token):
        """
        Usually flag_id and token are not used.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))

            s.send('w') # Write a new flag
            flag_id = self._random_str()
            token = self._random_str()
            fake_flag = 'NOTAFLAG' + self._random_str()
            s.send(flag_id + token)
            s.sendall(fake_flag + '\n')

            echo = recv_until(s, '\n').strip('\n')

            # Here we checks if the remote service is working normally. If the 
            # assertion fails, you might want to check the patch to the service.
            assert echo == fake_flag

            self.r = { 'FLAG_ID': flag_id,
                        'TOKEN': token,
                        'ERROR': 0,
                        'ERROR_MSG': ''
                     }

        except Exception as ex:
            # Ouch. SLA will be hurt!
            self.r = { 'FLAG_ID': flag_id,
                        'TOKEN': token,
                        'ERROR': 2,
                        'ERROR_MSG': 'Exception occurred: %s' % str(ex)
                     }


    def result(self):
        return self.r

def main():
    assert len(sys.argv) == 2
    ip = sys.argv[1]
    port = PORT # This is the normal port

    benign = Benign()
    benign.execute(ip, port, None, None)

    print benign.result()

if __name__ == "__main__":
    main()

