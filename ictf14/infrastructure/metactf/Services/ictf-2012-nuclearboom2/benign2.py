# TODO random interactions..
import random
import string
import sys

class Benign():

    DEFAULT_ERROR_CODE = 42

    def execute(self, ip, port, flag_id, token):

        from socket import socket


        error = -1
        error_msg = ''
        try:
            s = socket()
            s.connect((ip, port))
            error = self.DEFAULT_ERROR_CODE
            ans = self.do_benign(s)
            error = 0
        except Exception as e:
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
        #import IPython
        from utils import recv_until



        def get_random_plant_name():
            nameLen = random.randrange(4, 12)
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

        # Create a plant with a random name
        def build_plant():
            print "building plant"
            s.send('1\n')
            recv_until(s, 'Insert new plant name: ')
            s.send(get_random_plant_name() + '\n')
            recv_until(s, 'Insert new password: ')
            s.send(get_random_password() + '\n')
            recv_until(s, 'Insert new self-destruction code: ')
            s.send(get_random_selfdestruction() + '\n')
            return True

        def list_plants():
            print "listing plants"
            s.send('2\n')
            recv_until(s, 'Your choice: ')
            return True

        def display_plant_info():
            print "display plant info"
            s.send('3\n')
            recv_until(s, 'Insert plant ID:')
            # Send random plant id
            s.send("{0}\n".format(random.randrange(0, 10)))
            recv_until(s, 'Your choice: ')
            return True

        def edit_plant():

            def recv_until(s, endmsg):
                msg = ''
                while True:
                    part = s.recv(2048);
                    msg += part
                    if msg.find(endmsg) >= 0 or "level is too high" in msg:
                        break
                return msg

            print "editing plant"
            s.send('4\n')
            recv_until(s, 'Insert plant ID:')
            # Send random plant id
            s.send("{0}\n".format(random.randrange(0, 10)))
            recv_until(s, 'Choice:')
            # Select one of the 5 chemical elements [1-5]
            s.send("{0}\n".format(random.randrange(1,6)))
            recv_until(s, 'How much more (0-10000):')
            #s.send("{0}\n".format(random.randrange(0, 100000)))
            s.send(str(random.randrange(100, 4000)) + '\n')
            msg = recv_until(s, 'Your choice: ')
            # If "is too high" appears, that means that
            # the server just terminated our connection
            return not "is too high" in msg

        def get_destruct_code():
            print "get destruct code"
            s.send('5\n')
            recv_until(s, 'Insert plant ID: ')
            s.send(str(random.randrange(0,7)) + '\n')
            recv_until(s, 'Insert plant password: ')
            s.send(get_random_password() + '\n')
            recv_until(s, 'Your choice: ')
            return True

        def set_destruct_code():
            print "set destruct code"
            s.send('6\n')
            recv_until(s, 'Insert plant ID: ')
            s.send(str(random.randrange(0,7)) + '\n')
            recv_until(s, 'Insert plant password: ')
            s.send(get_random_password() + '\n')
            recv_until(s, 'Your choice: ')
            return True

        funcs = [build_plant, list_plants, display_plant_info, edit_plant, get_destruct_code, set_destruct_code]
        # And so it begins..
        recv_until(s, 'Your choice: ')
        random.shuffle(funcs)
        # Execute between 1-6 of them
        #for i in range(random.randrange(90,100)):
        for i in range(random.randrange(3, 8)):
            print 'current idx: %d' % i
            # The only time one of the functions returns false, is when
            # something unexpected happens and we should assume the connection is kaput.
            if not funcs[random.randrange(0, len(funcs))]():
                break
            print 'done!'
        else:
            # Exit properly half the time
            if random.randrange(0,1) == 0:
                s.send('7\n')
        s.close()


def main():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    b = Benign()
    b.execute(ip, port, '', '')
    b.result()


if __name__ == '__main__':
    main()
