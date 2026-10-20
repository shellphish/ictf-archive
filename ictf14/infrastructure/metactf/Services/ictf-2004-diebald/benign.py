import sys
import random

import requests

class Benign(object):        
    def __init__(self):
        self.error = 1
        self.error_msg = "execute() is not called."
        self.flag_id = ""
        self.token = ""

    def execute(self, ip, port, flag_id, token):
        url_base = "http://%s:%d/" % (ip, port)
        cgi_base = "http://%s:%d/cgi-bin/diebald.cgi" % (ip, port)
        action = random.randint(0, 3)

        if action == 0:
            # Browse HTMLs
            r = requests.get(url_base)
            if "Die-bald Corporation" not in r.text:
                self.error = 2
                self.error_msg = 'Incorrect front page'
                return

        elif action == 1:
            # Browse products.html
            r = requests.get(url_base + 'products.html')
            if 'UN Internet Voting System' not in r.text:
                self.error = 3
                self.error_msg = 'Incorrect products page'
                return

        elif action == 2:
            # Browse diebald.cgi
            r = requests.get(cgi_base)
            if 'Assign a task to a Die-Bald Administrator' not in r.text:
                self.error = 4
                self.error_msg = 'Incorrect diebald.cgi'
                return

        self.error = 0
        self.error_msg = ''
        self.flag_id = ""
        self.token = ""
        
    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

