import socket
from random import randint
from socket import SHUT_RDWR
from utility import CtfUtil
import sys
sys.path.insert(0,'.')

def rtil_str(s, st):
    buf = ""
    x = 0
    while True:
        curr = s.recv(1)
        if curr == "":
            break
        buf += curr
        if(curr == st[x]):
            x += 1
            if x == len(st):
                break
        else:
            x = 0
    return buf
    
class Benign():

    def get_free_port(self,sok,ip,start_port):
        while True:
            try:
                sok.bind((ip,start_port))
                break
            except:
                pass
            start_port = start_port + 1
        hex_str = hex(start_port)[2:]
        maxl = len(hex_str)
        if maxl%2 == 0:
            even = True
        else:
            even = False
        
        i = 0
        port_str = ''
        while i < maxl:
            if not even:
                even = True
                port_str += ',' + str(int(hex_str[i:i+1],16))
                i = i + 1
            else:
                port_str += ',' + str(int(hex_str[i:i+2],16))
                i = i + 2
        #port_str = port_str[1:]    
        return (start_port,port_str)
    
    def execute(self,ip,port,flag_id,token):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #l=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #start_port = 2020 + randint(0,1000)
        #You might have to change this, depending on your interface
        #(back_port, back_port_str) = self.get_free_port(l,"192.168.56.1",start_port)
        #print str((back_port, back_port_str))
        #l.listen(5)
        s.connect((ip,port))
        s.send("user ftp\n")
        s.send("pass pass\n")
        #print 'R1:' + s.recv(20)
        #print 'R1:' + rtil_str(s,'user logged in')
        s.send('PASV\n')
        #print 'Received:' + s.recv(10)
        pasv_resp = rtil_str(s,')')
        ip_ports = pasv_resp.split('(')[1].split(')')[0]
        ip_parts = ip_ports.split(',')
        to_connect_ip = ip_parts[0] + '.' + ip_parts[1] + '.' +ip_parts[2] + '.' +ip_parts[3]
        to_connect_port = (int(ip_parts[4]) << 8) + (int(ip_parts[5]))
        
        s.send("list -t \n")
        #print 'Trying to get list'
        clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        clientsocket.connect((to_connect_ip,to_connect_port))
        received=clientsocket.recv(1024)
        list=received
        while len(received)>0:
          received=clientsocket.recv(1024)
          list+=received
        clientsocket.close()
        #This is to revert the server in active mode
        #Note: any numbers are fine here
        s.send("port 8,8,8,8,34,34\n")
        s.send("QUIT\n")
        s.close()
        self.error = 0
        self.error_msg = ''
        self.flag_id = flag_id
        self.token = token
    
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
