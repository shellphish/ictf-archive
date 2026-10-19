class SetFlag():

    def execute(self, ip, port, flag):

        def get_random_string():
            import random
            import string
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))


        from socket import socket

        self.flag_id = get_random_string()
        self.cookie = get_random_string()

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
                'COOKIE' : self.cookie,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

    def do_setflag(self, s, ip, flag):
        import sys
        import struct
        from socket import socket
        import hashlib

        def gen_password(ip):
            team_id = ip.split('.')[3]
            password = hashlib.sha256('%s-mylittlesecret-%s' % (team_id, team_id)).hexdigest()
            return password

        def recv_until(s, endmsg):
            msg = ''
            while True:
                part = s.recv(2048);
                #print part,
                msg += part
                if part.find(endmsg) >= 0:
                    break
            return msg

        msg = recv_until(s, 'Your choice: ')
        print 'START'
        print msg
        print 'END'
        s.send('6\n')


        msg = recv_until(s, 'Password: ')
        password = gen_password(ip)
        print 'START'
        print msg
        print 'END'
        s.send('%s\n' % password)

        msg = recv_until(s, 'Insert new self-destruction code: ')
        print 'COMPLETE'
        print msg
        print 'YOUR TURN'
        s.send('%s\n' % flag)

        s.close()
