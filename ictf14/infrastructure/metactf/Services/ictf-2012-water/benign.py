class Benign():
  def execute(self, ip, port, flag_id, token):
    import socket
    import random
    import time
    import datetime

    def build_sequence():
      elements = []
      l = random.randint(1,100)
      seeds = []
      for i in range(l):
	seeds.append("")
      for seed in seeds:
	elements.append(int(seed+str(random.randint(0,2000000))))
      elements.sort()
      return ",".join([str(x) for x in elements])

    flag = ''
    error = -1
    error_msg = ''
 
    try:
      s = socket.socket()
      s.connect((ip,port))

      msg = s.recv(1024)

      s.send(build_sequence())
      msg = s.recv(1024)
      flag = None
      error = 0

    except Exception as e:
      error = 42
      error_msg = str(e)

    self.flag = flag
    self.error = error
    self.error_msg = error_msg

  def result(self):
    return {'FLAG' : self.flag,
	    'ERROR' : self.error,
	    'ERROR_MSG' : self.error_msg,
	   }
