#!/usr/bin/env python

import os
from SocketServer import ThreadingMixIn
from CGIHTTPServer import CGIHTTPRequestHandler 
from BaseHTTPServer import HTTPServer 

mydir = os.path.dirname(os.path.realpath(__file__))

class ThreadingCGIServer(ThreadingMixIn, HTTPServer):
    pass

def main():
    # Change dir
    os.chdir(mydir + "/html")

    server_address = ('0.0.0.0', 8014) 
    handler = CGIHTTPRequestHandler
    handler.cgi_directories = ["/cgi-bin"]
    httpd = ThreadingCGIServer(server_address, handler) 

    try:
        while True:
            httpd.handle_request()

    except Exception:
        pass

if __name__ == "__main__":
    main()
