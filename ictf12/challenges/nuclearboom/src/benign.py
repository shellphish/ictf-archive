# TODO random interactions..
class Benign():

    def execute(self, ip, port):

        from socket import socket

        error = -1
        error_msg = ''
        try:
            s = socket()
            s.connect((ip, port))
            ans = self.do_benign(s)
        except Exception as e:
            error = 42
            error_msg = str(e)

        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

    def do_benign(self, s):
        import sys
        import struct
        from socket import socket
        import IPython

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
        print 'COMPLETE'
        print msg
        print 'YOUR TURN'
        s.send('2\n')


        msg = recv_until(s, 'Your choice: ')
        print 'COMPLETE'
        print msg
        print 'YOUR TURN'
        s.send('3\n')

        msg = recv_until(s, 'Insert plant ID: ')
        print 'COMPLETE'
        print msg
        print 'YOUR TURN'
        s.send('10\n')

        s.close()
