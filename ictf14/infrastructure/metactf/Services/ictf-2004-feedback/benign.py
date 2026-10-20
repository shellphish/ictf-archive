import socket
import sys
import random
import os
sys.path.insert(0,'.')
random.seed(os.urandom(20))
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
        #return
        sf = SetFlag()
        print "HOst is", ip
        print "Port is", port
        flag = "FLG" +  CtfUtil.getRandomString(13)
        print "Flag is", flag
        sf.execute(ip,port,flag)
        res = sf.result()
        fid = res['FLAG_ID']
        t = res['TOKEN']
        print "Flag_ID is", fid
        print "Token is ", t
        if type(fid) != str :
            self.error = 1
            self.error_msg = 'ERROR in setting a flag' 
            
        self.flag_id = fid
        self.token = t
        #return
        cf = GetFlag()
        cf.execute(ip, port, fid, t)
        res = cf.result()
        res['FLAG'] = res['FLAG']
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

if __name__=="__main__":
    b=Benign()
    b.execute("localhost",8184,"ucsb%2C")
