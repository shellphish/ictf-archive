import traceback
import re

#import IPython


from utils import recv_until, get_id_from_plant_name


class GetFlag():

    def execute(self, ip, port, flag_id, token):

        from socket import socket
        import hashlib

        flag = ''
        error = -1
        error_msg = ''
        try:
            s = socket()
            s.connect((ip, port))
            error = 0

            flag = self.do_getflag(s, ip, flag_id, token)
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


    def do_getflag(self, s, ip, flag_id, token):
        import sys
        import struct
        from socket import socket
        import hashlib
        import re

        msg = recv_until(s, 'Your choice: ')

        plant_id = get_id_from_plant_name(s, flag_id)

        s.send('5\n')
        msg = recv_until(s, 'Insert plant ID: ')
        print 'received 1: %s' % msg
        s.send('%s\n' % plant_id)
        msg = recv_until(s, 'Insert plant password: ')
        print 'received: %s' % msg
        print 'sending password: "%s"' % token
        s.send('%s\n' % token)
        print 'START'
        print msg
        print 'END'

        msg = recv_until(s, 'Your choice: ')

        # parse the flag out
        m = re.search('secret self-destruction code is: "(\w+)". Handle with', msg)
        if m:
            flag = m.group(1)
            print 'FLAG DETECTED: %s' % flag
        else:
            print msg
            raise Exception('flag not found')
        s.close()

        return flag


if __name__ == "__main__":
    import sys
    getter = GetFlag()
    getter.execute(sys.argv[1],4444,sys.argv[2],sys.argv[3])
    if getter.error is 0:
        print "FLAG:%s" % getter.flag
    else:
        print "ERROR:%s" % getter.error_msg
