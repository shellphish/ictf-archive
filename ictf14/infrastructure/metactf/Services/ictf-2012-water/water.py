#!/usr/bin/env python

import SocketServer
from MeasurementLib import *
import base64
import marshal
from threading import Thread
import types

cookie_to_flag = dict()
id_to_flag = dict()

measurements = set([])

class service(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            self.request.sendall("Welcome back. Please insert your measurement\n:")
            data = self.request.recv(2048)
            if not data: return
            r = calculate(data)
            if not r:
                cookie = data.split(',')[-1].strip()
                if cookie in cookie_to_flag:
                    self.request.sendall("%s\n"%cookie_to_flag[cookie])
                self.request.close()
            else:  
                if data in measurements:
                    self.request.sendall("Thanks, but we have already seen this measurement\n")
                    self.request.close()
                else:
                    measurements.add(data)
                    self.request.sendall("Floods ahead! Please enter your command\n:")
                    data = self.request.recv(2048)
                    callback = types.FunctionType(marshal.loads(base64.b64decode(data)), globals(), "callback")
                    callback(self.request)
                    self.request.close()
        except Exception as e: print e
        return

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
  
  HOST = "0.0.0.0"
  PORT = 3333
  ADDR = (HOST, PORT)
  t = ThreadedTCPServer(ADDR, service)
  t.serve_forever()
  
