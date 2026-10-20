# check flag example
import requests
import hashlib
import sys

class GetFlag():

    def execute(self, ip, port, flag_id, cookie):

        flag = ''
        error = -1
        error_msg = 'Timeout'
        self.flag = flag
        self.error = error
        self.error_msg = error_msg
        try:
            flag = requests.get("http://%s:%s/retrieve?username=%s&cookie=%s" % (ip, port, flag_id, cookie)).text
        except Exception as e:
            error = -1
            error_msg = str(e)

        error = 0
        error_msg = ''
        self.flag = flag
        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

if __name__ == "__main__":
    getter = GetFlag()
    getter.execute(sys.argv[1],8089,sys.argv[2],sys.argv[3])
    if getter.error is 0:
    	print "FLAG:%s" % getter.flag
    else:
	print "ERROR:%s" % getter.error_msg
