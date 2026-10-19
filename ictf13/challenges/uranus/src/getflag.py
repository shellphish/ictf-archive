import requests
import json

class GetFlag():

    DEBUG = False

    def do_getflag(self, ip, port, flag_id, token):
        if self.DEBUG: print 'Getting flag..',
        r=requests.post("http://%s:%s/" % (ip, port), json.dumps({"flag_id": flag_id, "token": token}))
        if self.DEBUG: print r.text
        return r.text.strip()[15:]


    def execute(self, ip, port, flag_id, token):

        error = 0
        error_msg = ''
        try:
            flag = self.do_getflag(ip, port, flag_id, token)
        except Exception as e:
            error = 42
            error_msg = str(e)

        self.flag = flag
        self.error = error
        self.error_msg = error_msg


    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
if __name__== "__main__":
    import sys
    try:
        b = GetFlag()
        b.execute(sys.argv[1], 1337, sys.argv[2], sys.argv[3])
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
