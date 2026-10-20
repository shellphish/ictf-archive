# set flag example
import requests
import sys

class SetFlag():

    def execute(self, ip, port, flag):
        def get_random_flag_id():
            import random
            import string
            username = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))
            return '%s@gmail.com' % username

        def get_random_cookie():
            import random
            import string
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))

        flag_id = get_random_flag_id()
        cookie = get_random_cookie()
        error = -1
        error_msg = 'Timeout'
        self.flag_id = flag_id
        self.cookie = cookie
        self.error = error
        self.error_msg = error_msg
        try:
            resp = requests.get("http://%s:%s/store?username=%s&value=%s&cookie=%s" % (ip, port, flag_id, flag, cookie)).text
            if "OK" not in resp:
                error = 1
                error_msg = "Flag not updated"
            else:
                error = 0
                error_msg = ""
        except Exception as e:
            error = -1
            error_msg = str(e)

        self.flag_id = flag_id
        self.cookie = cookie
        self.error = error
        self.error_msg = error_msg


    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.cookie,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

if __name__ == "__main__":
    setter = SetFlag()
    setter.execute(sys.argv[1],8089,sys.argv[2])
    if setter.error is 0:
    	print "FLAG_ID:%s" % setter.flag_id
    	print "COOKIE:%s" % setter.cookie
    else:
	print "ERROR:%s" % setter.error_msg
