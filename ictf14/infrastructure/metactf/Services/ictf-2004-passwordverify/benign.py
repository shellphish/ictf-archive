import socket
import sys
import random
sys.path.insert(0,'.')
from setflag import SetFlag
from getflag import GetFlag
from utility import CtfUtil

class Benign():

    def do_benign(self, s, username, password):
        pass
        
    def execute(self, ip, port, flag_id, token):
        self.error = 0
        self.error_msg = ''
        self.flag_id = ""
        self.token = ""
        self.error = 0
        self.error_msg = None

        sf = SetFlag()
        flag = CtfUtil.getRandomString(random.randint(6,8))
        sf.execute(ip,port,flag)
        res = sf.result()
        flag_id = res['FLAG_ID']
        token = res['TOKEN']
        if type(flag_id) != str :
            self.error = 1
            self.error_msg = 'ERROR in setting a flag' 
            
        self.flag_id = flag_id
        self.token = token
        
        cf = GetFlag()
        cf.execute(ip, port, flag_id, token)
        res = cf.result()
        res['FLAG'] = res['FLAG'].rstrip()
        print res
        if flag != res['FLAG']:
            self.error = 2
            self.error_msg = 'ERROR in getting e flag'


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
