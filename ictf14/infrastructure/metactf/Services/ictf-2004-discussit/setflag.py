import random
import socket
import string

def random_string(length, alphabet=string.letters):
    return "".join(random.choice(alphabet) for i in range(length))

class SetFlag(object):
    def __init__(self):
        self.error = None
        self.error_msg = None
        self.flag_id = None
        self.token = None

    def execute(self, ip, port, flag):
        self.flag_id = random_string(random.randrange(6, 10))
        self.token = random_string(random.randrange(8, 12))

        # :note: We are working around that there is no flag_id-token tuple
        #        by concat'ing them.

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        to_send = "{}_{} {}\n".format(self.flag_id, self.token, flag)
        #print 'Sending:' + to_send
        s.send(to_send)
        s.close()

        self.error = 0
        self.error_msg = ""

    def result(self):
        return {'FLAG_ID': self.flag_id,
                'TOKEN': self.token,
                'ERROR': self.error,
                'ERROR_MSG': self.error_msg}
