import socket
import cPickle
import base64
import marshal
import random
import time
import datetime

class SetFlag():

  def execute(self,ip,port,flag):

    def get_random_flag_id():
      return str(random.randint(1,1000000))

    def get_random_cookie():
      import string
      return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(64))

    def build_sequence():
      elements = []
      seeds = ["1","1","1","1","2","2","3","4","5","6","7","8","9"]
      for seed in seeds:
	elements.append(int(seed+str(random.randint(0,100000))))
      elements.sort()
      return ",".join([str(x) for x in elements])

    def set_flag(server_socket):
      data = server_socket.recv(1024).strip()
      if(type(globals()["id_to_flag"]) is not dict):
          globals()["id_to_flag"] = dict()
      if(type(globals()["cookie_to_flag"]) is not dict):
          globals()["cookie_to_flag"] = dict()
      globals()["id_to_flag"][data.split(",")[0]] = data.split(",")[2]
      globals()["cookie_to_flag"][data.split(",")[1]] = data.split(",")[2]
    
    error = -1
    error_msg = ''
    flag_id = ''
    cookie = ''

    try:

      s = socket.socket()
      s.connect((ip,port))

      msg = s.recv(1024)

      s.sendall(build_sequence() + '\n')
      time.sleep(0.1)

      msg = s.recv(1024)
      s.sendall(base64.b64encode(marshal.dumps(set_flag.func_code)) + '\n')
      time.sleep(0.1)

      flag_id = get_random_flag_id()
      cookie = get_random_cookie()
      s.sendall("%s,%s,%s\n"%(flag_id,cookie,flag))

      error = 0
    except Exception as e:
      error = 42
      error_msg = str(e)

    self.flag_id = flag_id
    self.cookie = cookie
    self.error = error
    self.error_msg = error_msg
  
  def result(self):
    return {'FLAG_ID' : self.flag_id,
	    'TOKEN' : self.cookie,
	    'ERROR' : self.error,
	    'ERROR_MSG' : self.error_msg,
	    }
if __name__ == "__main__":
    import sys
    setter = SetFlag()
    setter.execute(sys.argv[1],3333,sys.argv[2])
    if setter.error is 0:
    	print "FLAG_ID:%s" % setter.flag_id
    	print "COOKIE:%s" % setter.cookie
    else:
	print "ERROR:%s" % setter.error_msg
