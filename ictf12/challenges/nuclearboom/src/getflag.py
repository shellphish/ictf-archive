import traceback
import re

class GetFlag():

    def execute(self, ip, port, flag_id, cookie):

        from socket import socket
        import hashlib

        flag = ''
        error = -1
        error_msg = ''
        try:
            s = socket()
            s.connect((ip, port))
            error = 0

            flag = self.do_getflag(s, ip, flag_id, cookie)
        except Exception as e:
            error = 1
            error_msg = str(e)
            error_msg += traceback.format_exc()

        self.flag = flag
        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }


    def do_getflag(self, s, ip, flag_id, cookie):
        import sys
        import struct
        from socket import socket
        import hashlib

        def gen_password(ip):
            print 'IP', ip
            team_id = ip.split('.')[3]
            password = hashlib.sha256('%s-mylittlesecret-%s' % (team_id, team_id)).hexdigest()
            return password

        def recv_until(s, endmsg):
            msg = ''
            while True:
                part = s.recv(2048);
                msg += part
                if part.find(endmsg) >= 0:
                    break
            return msg

        msg = recv_until(s, 'Your choice: ')
        print 'START'
        print msg
        print 'END'
        s.send('5\n')

        msg = recv_until(s, 'Password: ')
        password = gen_password(ip)
        print 'START'
        print msg
        print 'END'
        s.send('%s\n' % password)

        msg = recv_until(s, 'Control Panel:')
        print 'START'
        print msg
        print 'END'

        for line in msg.split('\n'):
            if line.find('The uber-duber secret self-destruction code is:') >= 0:
                import re
                m = re.search('"(\w+)"', line)
                flag = m.group(1)


        return flag

        s.close()
