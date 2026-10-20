import socket
import sys
sys.path.insert(0,'.')
from utility import pybrowse
class Benign():

        
    def execute(self, ip, port, flag_id, token):
        self.error = 0
        self.error_msg = ''
        self.flag_id = ""
        self.token = ""
        self.flag_id = flag_id
        self.token = token
        self.error = 0
        self.error_msg = None
        
    def result(self):
        if self.error == 0:
            return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
        else:
            return {
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
