#!/usr/bin/env python
import sys,random,os
sys.path.insert(0,".")
from common import MuleUser
random.seed(os.urandom(20))

class GetFlag():
  def execute(self, ip, port, flag_id, token):
    user = MuleUser(ip)
    self.flag = user.getFlag(token,flag_id)
    self.error = 0
    self.error_msg = ""

  def result(self):
    return {'FLAG' : self.flag,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }
