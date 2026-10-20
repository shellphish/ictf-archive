import random
import re
import socket
import string
import time

def random_string(length, alphabet=string.letters):
    return "".join(random.choice(alphabet) for i in range(length))

class GetFlag(object):
    def __init__(self):
        self.error = None
        self.error_msg = None
        self.flag = None

    def execute(self, ip, port, flag_id, token):
        time.sleep(.5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))

        # :note: We are working around that there is no flag_id-token tuple
        #        by concat'ing them.

        s.send("{}_{}\n".format(flag_id, token))
        received = s.recv(1024)
        while "else" not in received:
            received += s.recv(1024)

        for line in received.split("\n"):
            if not line.startswith("Last time"):
                continue
            regex = r"Last time we were talking about (?P<flag>.*)"
            match = re.match(regex, line)
            self.flag = match.group("flag")
        s.close()

        # Reset the flag
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send("{}_{} {}\n".format(flag_id, token, self.flag))
        s.close()

        self.error = 0
        self.error_msg = ""

    def result(self):
        return {'FLAG': self.flag,
                'ERROR': self.error,
                'ERROR_MSG': self.error_msg}
