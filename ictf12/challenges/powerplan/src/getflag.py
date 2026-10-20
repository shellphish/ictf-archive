from socket import socket
import re

class GetFlag():

    DEFAULT_ERROR_CODE = 42 

    """
    Blocks until data is received that matches the given regex
    """
    def wait_for_regex(self, regex):
        compiled_regex = re.compile(regex)
        while True:
            data = self.sock_file.readline()
            if(len(data)==0):
                raise Exception("Exit")
            elif (compiled_regex.match(data)):
              break;

    def execute(self, ip, port, flag_id, cookie):

        self.flag = ''
        # An error code of -1 means the service is down
        self.error = -1
        self.error_msg = ''

        try:
            self.sock = socket()
            self.sock.connect((ip, port))
            self.error = self.DEFAULT_ERROR_CODE
            self.sock_file = self.sock.makefile()
            print self.recv_msg()
            self.send_msg("L")
            print self.recv_msg()
            # Login with flag_id as username and cookie as passwd
            self.send_msg(flag_id)
            print self.recv_msg()
            self.send_msg(cookie)
            self.wait_for_regex(r"^Your previous victory message")
            self.flag = self.recv_msg()

            # Everything worked. Set error to 0
            self.error = 0
        except Exception as e:
            self.error_msg = str(e)

    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

    def send_msg(self, data):
        self.sock.sendall(data + "\n")
    
    def recv_msg(self):
        data = self.sock_file.readline()
        if(len(data)==0):
            raise Exception("Exit")
        return data.strip()
