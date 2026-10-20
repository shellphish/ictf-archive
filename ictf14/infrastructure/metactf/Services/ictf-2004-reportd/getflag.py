import socket
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))
    response=sock.recv(1024)
    sock.send("2\n")
    sock.send(token+"\n")    
    while(response.find("continue")==-1):
      response+=sock.recv(1024)
    sock.close()
    self.flag = None
    for curr_line in response.split('\n'): 
        if flag_id in curr_line:
            for curr_wrd in curr_line.split():
                if curr_wrd.startswith(flag_id):
                    self.flag = curr_wrd[len(flag_id+':'):]
    
    
    #self.flag=response[response.find("Your report:")+13:][:16]
    #print 'GetFlag:' + response
    self.error=0;self.error_msg=""
    if self.flag == None:
        self.flag = ''
        self.error = -1
        self.error_msg = 'Flag not found'
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
