import random,time,string
import requests

class SetFlag(object):
    def __init__(self):
        self.token = ""
        self.flag_id = ""
        self.error = 1
        self.error_msg = "execute() is not called."

    def execute(self, ip, port, flag):
        name = "".join([ random.choice(string.letters) for i in xrange(random.randint(6,8)) ])
        password = "".join([ random.choice(string.letters + string.digits) for i in xrange(6) ])
        
        url_base = "http://%s:%d/cgi-bin/diebald.cgi" % (ip, port)
        r = requests.get(url_base, params={'op': 'create', 
                                        'username': name, 
                                        'password': password
                                      }
        )

        if "Account successfully created" not in r.text:
            self.error = 2
            self.error_msg = "Cannot create account."
            return

        r = requests.get(url_base, params={'op': 'addtask', 
                                        'username': name, 
                                        'password': password, 
                                        'task': flag
                                      }
        )
        if "was assigned to user" not in r.text:
            self.error = 3
            self.error_msg = "Cannot assign task to a user"
            return

        self.token = password
        self.flag_id = name
        self.error = 0
        self.error_msg = ""

    def result(self):
        return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}

if __name__ == "__main__":
    import sys
    sf = SetFlag()
    sf.execute(sys.argv[1], 8012, sys.argv[2])
    print sf.result()
