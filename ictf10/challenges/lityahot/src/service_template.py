#! /usr/bin/env python2.5
import sys
import os
import getopt
import socket
import threading
import select
import logging
import signal

debug = 0

ERRPARAMS = 2
ERRSOCKET = 3

def usage(fname):
    print "%s [-d (debug)] -p <port>" % fname

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class ClientManager(threading.Thread):
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('manager')
        
    def run(self):
        if debug:
            self.logger.debug("Thread manages client %s" % str(self.address))

        while True:
            try:
                infd = self.socket.makefile()
                msg = infd.readline().strip()
                (head, tail) = os.path.split(msg)
                outfd = open(tail)
                buf = outfd.read()
                self.socket.send(buf)
            except Exception, err:
                self.logger.debug("Terminating (%s)..." % str(err))
                self.socket.close()
                break
        self.logger.debug("Exiting...")
        return  

def cleanup(signum, frame):
    global req_termination
    logger = logging.getLogger('server')
    logger.debug("Received %d. Cleaning up..." % signum)
    sys.exit(0)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    global debug

    port = None
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger('server')
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "dhp:")
        except getopt.error, msg:
            raise Usage(msg)
        for o, a in opts:
            if o == "-d":
                debug = 1
            if o == "-h":
                usage(os.path.basename(argv[0]))
                return 1
            if o == "-p":
                port = int(a)
    except Usage, err:
        logger.error("%s -- for help use -h" % err.msg)
        return ERRPARAMS

    if port == None:
        logger.error("Missing port number")
        usage(os.path.basename(argv[0]))
        return ERRPARAMS
    # Sets the signal
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    if debug:
        logger.debug("listening on port %d" % port)
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(("0.0.0.0", port))
        serversocket.listen(5)
    except Exception, err:
        logger.error("Cannot create socket on port %d: %s" % (port, str(err)))
        return ERRSOCKET
    
    while True:
        (clientsocket, address) = serversocket.accept()
        ct = ClientManager(clientsocket, address)
        ct.start()

if __name__ == "__main__":
    sys.exit(main())
