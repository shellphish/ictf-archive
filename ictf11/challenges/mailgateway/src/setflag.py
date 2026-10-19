#!/usr/bin/env python
import sys,os,random
sys.path.insert(0,".")
random.seed(os.urandom(20))
from common import MuleUser

class SetFlag():
  def execute(self, ip, port, flag):
    user = MuleUser(ip)
    self.token,self.flag_id = user.setFlag(flag)
    self.error = 0
    self.error_msg = ""

  def result(self):
    return {'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }
