class GetFlag():
  def execute(self, ip, port, flag_id, cookie):
    import socket
    import random
    import time
    import datetime

    def build_sequence():
      elements = []
      seeds = ["","","","","","","","","","","","",""]
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

      s.sendall(build_sequence()+",%s\n"%cookie)
      msg = s.recv(1024)
      flag = msg.strip("\n")
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
if __name__ == "__main__":
    import sys
    getter = GetFlag()
    getter.execute(sys.argv[1],3333,sys.argv[2],sys.argv[3])
    if getter.error is 0:
    	print "FLAG:%s" % getter.flag
    else:
	print "ERROR:%s" % getter.error_msg
