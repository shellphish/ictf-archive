#! /usr/bin/env python
import sys
import os
import getopt
import socket
import threading
import select
import logging
import signal
import random
import sqlite3

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
        # TODO: Create a timer to kill a thread if it takes too long
        if debug:
            self.logger.debug("Thread manages client %s" % str(self.address))
        try:
            conn = sqlite3.connect(self.dbfile)
            cur = conn.cursor()
            infd = self.socket.makefile()
            self.socket.send("USER: ")
            user = infd.readline().strip()
            self.socket.send("COMMAND: ")
            cmd = infd.readline().strip()
            if cmd == "UPLOAD":
                self.socket.send("SHARED: ")
                shared = infd.readline().strip()
                if not (shared in ("true", "false")):
                    self.socket.send("""Only "true" and "false" are acceptable values\n""")
                    raise Exception("Invalid value")
                self.socket.send("FIRST: ")
                first = infd.readline().strip()
                self.socket.send("LAST: ")
                last = infd.readline().strip()
                self.socket.send("ADDRESS: ")
                address = infd.readline().strip()
                self.socket.send("IMAGE: ")
                buf = ""
                while True:
                    res = self.socket.recv(1)
                    if res == "":
                        break
                    buf = buf + res
                image_filename = os.tempnam("data", "mug")
                f = open(image_filename, "w+")
                f.write(buf)
                f.close()
                wantedid = random.randint(0,10000)
                cur.execute("""insert into wanted values (?, ?, ?, ?, ?, ?);""",
                            (wantedid, first, last, address, user, shared))
                cur.execute("""insert into mugshot values (?, ?);""",
                            (last, image_filename))
                conn.commit()
            elif cmd == "LIST":
                cur.execute("""select * from wanted where shared='true' or user=?;""", (user, ))
                self.socket.send("% 6s % 20s % 20s % 40s\n" % ("ID", "FIRST", "LAST", "ADDRESS"))
                for row in cur:
                    self.socket.send("% 6s % 20s % 20s % 40s\n" % (row[0], row[1], row[2], row[3]))
            elif cmd == "MUGSHOT":
                self.socket.send("ID: ")
                wantedid = infd.readline().strip()
                cur.execute("""select last from wanted where id=?;""", (wantedid, ))
                for row in cur:
                    last = row[0]
                cur.execute("""select image from mugshot where last='%s';""" % last)
                for row in cur:
                    filename = row[0]
                self.socket.send(open(filename).read())
                self.socket.send("\n")
            else:
                self.socket.send("COMMANDS: LIST UPLOAD MUGSHOT\n")
            cur.close()
            conn.close()
            self.socket.send("Transaction terminated\n")
            self.socket.close()
        except Exception, err:
            self.logger.debug("Terminating with exception (%s)..." % str(err))
            if cur: cur.close()
            if conn: conn.close()
            if self.socket: self.socket.send("There was an exception\n")
            self.socket.close()
            return
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

    port = 2048
    dbfile = "wanted.db"
    initialize = False
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger('server')
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "dhp:ib:")
        except getopt.error, msg:
            raise Usage(msg)
        for o, a in opts:
            if o == "-d":
                debug = 1
            if o == "-h":
                usage(os.path.basename(argv[0]))
                return 1
            if o == "-i":
                initialize = True
            if o == "b":
                dbfile = a
            if o == "-p":
                port = int(a)
    except Usage, err:
        logger.error("%s -- for help use -h" % err.msg)
        return 1
    if initialize:
        try:
            file = open(dbfile, "w+")
            file.close()
            conn = sqlite3.connect(dbfile)
            cur = conn.cursor()
            cur.execute("""create table wanted (id int, first text, last text, address text, user text, shared text);""")
            cur.execute("""create table mugshot (last text, image text);""")
            cur.execute("""create table mgmtfile (filename text, manager text);""")
            data =  ((18219, "Massimo", "Zanardi", "17 Via Pazienza, Bologna, Italy", "unknown", "true"),
                     (71823, "Guglielmo", "de Roberti", "87 Telegraph Road, Berkeley, CA, USA", "unknown", "true"),
                     (61511, "Fredrik", "Mays", "111 Via Golgi, Milan, Italy", "krueger", "true"),
                     (61799, "Adamo", "Duped", "98 Terrrace Ln, Santa Barbara, CA, USA", "krueger", "false"),
                     (88715, "Cristiano", "Aquila", "181 Runaway Rd, Monterey, CA, USA", "unknown", "false"),
                     (79956, "Mark", "Broods", "783 Greenwich St, Birmingham, AL, USA", "unknown", "false"))
            for datum in data:
                cur.execute("""insert into wanted values (?, ?, ?, ?, ?, ?);""", datum)
            mugs =  (("Zanardi", "zanardi.jpg"),
                     ("de Roberti", "deroberti.jpg"),
                     ("Mays", "mays.jpg"),
                     ("Duped", "duped.jpg"),
                     ("Aquila", "aquila.jpg"),
                     ("Broods", "broods.jpg"))
            for mug in mugs:
                cur.execute("""insert into mugshot values (?, ?);""", mug)
            mgmtfiles =  (("secret.txt", "Lisvoy Bironulesk"),
                          ("wiretaps.txt", "Femily Edeo"),
                          ("finance.txt", "Brostem Ubosi"))
            for mgmtfile in mgmtfiles:
                cur.execute("""insert into mgmtfile values (?, ?);""", mgmtfile)
            conn.commit()
            cur.close()
        except Exception, err:
            logger.error("Failed to initialize the database: %s" % str(err))
            return 1

    # Makes sure that the database exists
    try:
        conn = sqlite3.connect(dbfile)
    except:
        logger.error("Cannot open database %s" % dbfile)
        return 1
    if debug:
        cur = conn.cursor()
        cur.execute("""select * from wanted;""")
        print "*** TABLE wanted"
        for row in cur:
            print("%s %s %s %s %s %s" % (row[0], row[1], row[2], row[3], row[4], row[5]))
        cur.execute("""select * from mugshot;""")
        print "*** TABLE mugshot"
        for row in cur:
            print("%s %s" % (row[0], row[1]))
        cur.execute("""select * from mgmtfile;""")
        print "*** TABLE mgmtfile"
        for row in cur:
            print("%s %s" % (row[0], row[1]))
        cur.close()
    conn.close()

    ClientManager.dbfile = dbfile
    
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
        return 1
    
    while True:
        (clientsocket, address) = serversocket.accept()
        ct = ClientManager(clientsocket, address)
        ct.start()
    # Never reached
    return 0

if __name__ == "__main__":
    sys.exit(main())
