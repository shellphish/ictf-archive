import random
import string
from collections import OrderedDict

import requests

def random_string(n):
    return "".join([ random.choice(string.lowercase + string.uppercase + string.digits) for i in xrange(n) ])

class Benign(object):
    def __init__(self):
        self.error = 1
        self.error_msg = 'execute() is not called'

    def execute(self, ip, port, flag_id, token):
        url_base = "http://%s:%d/cgi-bin/" % (ip, port)
        action = random.randint(0, 4)

        if action == 0:
            # Browse the front page
            r = requests.get(url_base + 'guestbook.py')
            if 'Sign my guestbook' not in r.text:
                self.error = 2
                self.error_msg = 'Front page is not working'
                return

        elif action == 1:
            # Browse the cprog
            r = requests.get(url_base + 'cprog')
            if 'Unknown command' not in r.text:
                self.error = 3
                self.error_msg = 'cprog is not working'
                return

        elif action == 2:
            # Submit a public comment
            name = random_string(random.randint(4, 10))
            comment = random_string(random.randint(8, 30))
            r = requests.get(url_base + 'guestbook.py', params=OrderedDict([('name', name), ('comment', comment), ('command', 'sign')]))
            if 'Thanks for signing my guestbook' not in r.text:
                self.error = 4
                self.error_msg = 'Publishing comments is not working'
                return

        elif action == 3:
            # Submit a private comment
            name = random_string(random.randint(4, 10))
            comment = random_string(random.randint(8, 30))
            r = requests.get(url_base + 'guestbook.py', params=OrderedDict([('name', name), ('comment', comment), ('priv', 'on'), ('command', 'sign')]))
            if 'Thanks for signing my guestbook' not in r.text:
                self.error = 5
                self.error_msg = 'Publishing comments is not working'
                return

        self.flag_id = flag_id
        self.token = token
        self.error = 0
        self.error_msg = None
        
    def result(self):
        return {
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

if __name__ == '__main__':
    import sys
    be = Benign()
    be.execute(sys.argv[0], 8014, None, None)
    print be.result()

