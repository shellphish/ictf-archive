import socket
import sys
import base64
import multiprocessing
import datetime
import os
from multiprocessing import Lock, Manager
import string
import random
sys.path.insert(0,".")
from setflag import SetFlag
from getflag import GetFlag
from utility.CtfUtil import *
random.seed(os.urandom(20))


class Benign():
    def __init__(self):
        self.sf = SetFlag()
        self.gf = GetFlag()


    def execute(self, ip, port, flag_id, token):
        sf = self.sf
        gf = self.gf
        self.flag_id = None
        error = 0
        self.token = None
        self.error = 0
        self.error_msg = ""
        flag = "FLG" + getRandomString(13)
        self.error_msg = None
        sf.execute(ip, port, flag )
        sfresult = sf.result()
        if sfresult["ERROR"] != 0:
            self.error = sfresult["ERROR"]
            self.error_msg = "cannot set flag"
        else:
            gf.execute(ip, port, sf.flag_id, sf.token)
            gfresult = gf.result()
            if gfresult["ERROR"] != 0:
                self.error = sfresult["ERROR"]
                self.error_msg = "cannot get flag"
            else:
                read_token = gfresult["FLAG"]
                if read_token != flag:
                    self.error = 42
                    self.error_msg = "cannot retrieve the same flag"



        if error == 0:
            self.flag_id = flag_id
            self.token = token
            self.error = 0
            self.error_msg = ""

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
