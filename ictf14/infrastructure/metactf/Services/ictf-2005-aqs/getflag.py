from collections import OrderedDict
import re

import requests

class GetFlag(object):
    def __init__(self):
        self.flag = ''
        self.error = 1
        self.error_msg = 'execute() is not called'

    def execute(self, ip, port, flag_id, token):
        name = flag_id + '_' + token
        cgi_url = "http://%s:%d/cgi-bin/guestbook.py" % (ip, port)

        r = requests.get(cgi_url + '?name=' + name + '&command=lookup')

        m = re.search(r"<b> (\S+) </b>:\s+(\S+)\s+<br>", r.text)
        if m is None:
            self.error = 2
            self.error_msg = 'Flag is not found.'
            return

        returned_name, flag = m.group(1), m.group(2)
        if returned_name != name:
            self.error = 3
            self.error_msg = 'Service is not working correctly. Incorrect flag_id is returned.'
            return

        self.flag = flag
        self.error = 0
        self.error_msg = ""

    def result(self):
        return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}

if __name__ == "__main__":
    import sys
    s = GetFlag()
    s.execute(sys.argv[1], 8014, sys.argv[2], sys.argv[3])
    print s.result()

