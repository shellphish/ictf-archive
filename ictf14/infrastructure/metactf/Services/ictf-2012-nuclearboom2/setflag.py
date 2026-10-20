import random
import string

from utils import recv_until

class SetFlag():

    def execute(self, ip, port, flag):

        def get_random_string():
            import random
            import string
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))


        from socket import socket

        self.flag_id = get_random_string()
        self.token = get_random_string()

        error = -1
        error_msg = ''
        try:
            s = socket()
            s.connect((ip, port))
            error = 0
            ans = self.do_setflag(s, ip, flag)
        except Exception as e:
            error = 1
            error_msg = str(e)

        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {
                'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

    def do_setflag(self, s, ip, flag):
        import sys
        import struct
        from socket import socket
        import hashlib


        msg = recv_until(s, 'Your choice: ')
        print 'START'
        print msg
        print 'END'
        s.send('1\n')

        def get_random_plant_name():
            nameLen = random.randrange(6, 16)
            options = string.ascii_lowercase + string.ascii_uppercase + string.digits
            return ''.join(random.choice(options) for x in range(nameLen))

        def get_random_password():
            pwdLen = random.randrange(6, 12)
            options = string.ascii_lowercase + string.ascii_uppercase + string.digits
            return ''.join(random.choice(options) for x in range(pwdLen))

        def get_random_selfdestruction():
            pwdLen = random.randrange(6, 12)
            options = string.ascii_lowercase + string.ascii_uppercase + string.digits
            return ''.join(random.choice(options) for x in range(pwdLen))

        plant_name = get_random_plant_name()
        token = get_random_password()

        msg = recv_until(s, 'Insert new plant name: ')
        s.send(plant_name + '\n')

        msg = recv_until(s, 'Insert new password: ')
        s.send(token + '\n')

        print 'START'
        print msg
        print 'END'

        msg = recv_until(s, 'Insert new self-destruction code: ')
        print 'COMPLETE'
        print msg
        print 'YOUR TURN'
        s.send('%s\n' % flag)

        msg = recv_until(s, 'Your choice: ')

        s.close()

        self.flag_id = plant_name
        self.token = token
        self.error = 0
        self.error_msg = ''


if __name__ == "__main__":
    import sys
    setter = SetFlag()
    setter.execute(sys.argv[1],4444,sys.argv[2])
    if setter.error is 0:
        print "FLAG_ID:%s" % setter.flag_id
        print "TOKEN:%s" % setter.token
    else:
        print "ERROR:%s" % setter.error_msg
