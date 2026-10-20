import random
import string
from collections import OrderedDict

import requests

def getRandomString(n):
    return "".join([ random.choice(string.lowercase + string.uppercase + string.digits) for i in xrange(n) ])

class SetFlag(object):
    def __init__(self):
        self.flag_id = ''
        self.token = ''
        self.error = 1
        self.error_msg = 'execute() is not called'

    def execute(self, ip, port, flag):
        token = getRandomString(random.randint(6,8))
        flag_id = getRandomString(10)

        name = flag_id + '_' + token

        cgi_base = "http://%s:%d/cgi-bin/guestbook.py" % (ip, port)
        r = requests.get(cgi_base + '?name=' + name + '&comment='+ flag +'&priv=on&command=sign')
        if 'Thanks for signing' not in r.text:
            self.error = 2
            self.error_msg = 'Incorrect data returned from the service.'
            return

        self.flag_id = flag_id
        self.token = token
        self.error = 0
        self.error_msg = ""

    def result(self):
        return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}

if __name__ == "__main__":
    import sys
    s = SetFlag()
    s.execute(sys.argv[1], 8014, sys.argv[2])
    print s.result()
