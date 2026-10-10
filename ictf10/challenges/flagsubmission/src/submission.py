#!/usr/bin/env python

import sys
import os
import getopt
import BaseHTTPServer
import urlparse
import socket
import cgi
import logging
import random
import traceback
import glob
import urllib
import urllib2
import hashlib
import tempfile
import sqlite3
import time
import ConfigParser
import SocketServer
import threading
import base64
from subprocess import Popen, PIPE

# flags expire after 2 minutes
flag_expiry = 60 * 5
score_keeper = "http://scorekeeper/exploit?"

def update_scorekeeper(team, point_amount, service_name):
    address = score_keeper + urllib.urlencode({"team" : team, "credentials" : "getthatflagdude", "points" : point_amount, "service" : service_name})
    result = urllib.urlopen(address).read()
    return result == 'SUCCESS\n'

def verify_flag(base_64_flag):
    # First base64 decode the binary
    try:
        base_64_flag = base_64_flag[3:]
        base_64_decoded = base64.b16decode(base_64_flag)
    except TypeError:
        return None

    # Run it through gpg
    gpg = Popen(['/usr/bin/gpg', '--batch', '--yes' , '--passphrase-file', '../ScoreBot/pass', '-d', '--cipher-algo', 'AES256', ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = gpg.communicate(base_64_decoded)
    if gpg.returncode != 0:
        return None

    split = stdout.split('\n')

    if len(split) != 4:
        return None

    return split
    

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer): pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # A class-level lock to be used for synchronization
    lock = threading.Lock()

    # Paths to the resources
    home_path = "/"
    css_path = "/style.css"
    icon_path = "/favicon.ico"
    icon_file = "webserver.ico"
    submission_path = "/submission"
    dump_path = "/dump"

    # Parameters for accessing the database dump
    dump_auth_attr = "auth"
    dump_auth_value = "s3cr3t"

    # Secret used to generate sessions
    secret = "WhatIsASecretPhrase?CanYouEatIt?"

    # Header and footer
    header = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>%s</title>
    <link href='""" + css_path + """' rel="stylesheet" type="text/css" />
  </head>

  <body>
    <div id="content">
      <div id="banner">
        %s
      </div>

      <div id="main">
"""
    footer = """
      </div>
      <div id="footer">
        <p>[<a href='%s'>Home</a>]</p>
      </div>
    </div>
  </body>
</html>
""" % (home_path)

    # Sanitizes input from the user
    def sanitize(self, string):
        allowed = " '.,:;!?()-/_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if string == None:
            return ""
        newstring = ""
        for c in string:
            if c in allowed:
                newstring = newstring + c
        return newstring


    # Returns the CSS style file
    def style(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()

        self.wfile.write("""
body {
n  font-family: arial, sans-serif;
  font-size: 12pt;
  background: white;
  color: gray;
}

#content {
  border: 4px solid #CFCFCF;
  width: 800px;
  margin-top: 2em;
  margin-left: auto;
  margin-right:auto;
}

#banner {
  padding: 1em 1em 1em 1em;
  border: 0px solid red;
  background: #BABABA;
  text-align: center;
}

#main {
  padding: 1em 1em 1em 1em;
  border: 0px solid blue;
}

#footer {
  border: 0px solid yellow;
  font-size: 8pt;
  padding: 1em 1em 1em 1em;
  text-align: center;
}
""")
        return


    # Returns the favicon.ico icon
    def icon(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'image/vnd.microsoft.icon')
        self.end_headers()

        try:
            f = open(self.icon_file, "r")
            self.wfile.write(f.read())
        except Exception, err:
            self.logger.debug("Cannot open icon: %s" % str(err))
            
    def ip_to_team (self, ip):
      pfx24 = '.'.join(ip.split('.')[:-1])
      if pfx24 in self.ip_teams:
        return self.ip_teams[pfx24]
      else:
        return None


    # Prints the home page
    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Flag Submission", "Submit yer flags!"))

        self.wfile.write("""
<fieldset>
  <legend>Flag Submission</legend>
  <form action='%s' method='post'>
    <p>Flag: <input type="text" name="flag" /></p>
    <p><input type="submit" name="submit" value="Submit Flag!"></p>
  </form>
</fieldset>
""" % self.submission_path) 

    def dump(self, params):

        # Checks that the right credentials were provided
        if not params.has_key(self.dump_auth_attr) or params[self.dump_auth_attr][0] != self.dump_auth_value:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Dumps the database
        self.wfile.write(self.header % ("Database", "The Database"))
        self.wfile.write("""
<table summary="db">
  <thead>
    <tr><td>team short name</td><td>service</td><td>tick</td></tr>
  </thead>
  <tbody>
""")        

        cur = self.conn.cursor()
        cur.execute("""select * from submitted""")
        for row in cur:
            self.wfile.write("    <tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2]))
        cur.close()

        self.wfile.write("""
  </tbody>
</table>
""")
        self.wfile.write(self.footer)
        return

    def submission(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.header % ("Flag Submitted", "Flag Submitted"))

        flag = form.getfirst("flag")

        client_ip = self.client_address[0]
        team = self.ip_to_team(client_ip)
        if not team:
            team = "TESTING I AM NOT A TEAM"

        decrypted_flag = verify_flag(flag)
        if not decrypted_flag:
            self.wfile.write("Not a vaild flag!")
            self.wfile.write(self.footer)
            return

        
        service_name = decrypted_flag[0]
        tick = decrypted_flag[1]
        is_active = decrypted_flag[2] == "True"
        timestamp = float(decrypted_flag[3])

        # test if flag is still active
        current_time = time.time()
        if (timestamp + flag_expiry) < current_time:
            self.wfile.write("""Flag has expired!<br>Go hack something!""")
            self.wfile.write(self.footer)
            return

        cur = self.conn.cursor()
        cur.execute(""" select * from submitted where team_short_name=? and service=? and tick=?;""", (team, service_name, tick))
        if not cur.fetchone() == None:
            self.wfile.write("""You've already submitted that flag.<br>Go hack something!""")
            self.wfile.write(self.footer)
            return

        with RequestHandler.lock:
            cur.execute(""" insert into submitted values (?,?,?);""", (team, service_name, tick))
            self.conn.commit()
            cur.close()

        point_amount = self.points[service_name]
        if is_active:
            self.wfile.write("""Congrats, you got """ + str(point_amount) + """ points for submitting the flag. """)
        else:
            point_amount *= -1
            self.wfile.write("""Bzzzzzttt! Service was not active!<br>You lost """ + str(point_amount) + """ points for submitting an inactive flag.""")
            
        # This is where I'll update the score keeper with the amount
        update_scorekeeper(team, point_amount, service_name)

        self.wfile.write(self.footer)
        return
            
            
    def do_GET(self):
        try:
            self.logger.debug("Received GET request with path: %s" %  self.path)

            # Since this is a multi-threaded server each instance has to have its own db connection
            try:
                self.conn = sqlite3.connect(RequestHandler.db)
                cur = self.conn.cursor()
            except Exception, e:
                self.logger.error("Missing or corrupted database %s: %s" % (RequestHandler.db, str(e)))
                return 

            # Parses the request
            req = urlparse.urlparse(self.path)
            self.logger.debug("Received request resource: %s" % req.path)
            if self.headers.has_key("User-Agent"):
                self.logger.debug("Request User-Agent: %s" % self.headers['User-Agent'])

            params = urlparse.parse_qs(req.query)
            self.logger.debug("Received parameters: %s" % str(params))

            # Dispatches the request to the appropriate method
            if req.path == self.home_path:
                self.home(params)
                return

            elif req.path == self.css_path:
                self.style(params)
                return

            elif req.path == self.icon_path:
                self.icon(params)
                return

            elif req.path == self.dump_path:
                self.dump(params)
                return

            else:
                self.send_error(404,'Resource Not Found: %s' % self.sanitize(self.path))                
                return
            # Never reached
            return
        except Exception, err:
            self.wfile.write("An error occurred: " + self.sanitize(str(err)))
            self.logger.error("An error occurred: " + str(err))
            if debug:
                et, ev, tb = sys.exc_info()
                traceback.print_tb(tb)
            return


    def do_POST(self):
        try:
            self.logger.debug("Received POST request with path: %s" %  self.path)

            # Since this is a multi-threaded server each instance has to have its own db connection
            try:
                self.conn = sqlite3.connect(RequestHandler.db)
                cur = self.conn.cursor()
            except Exception, e:
                self.logger.error("Missing or corrupted database %s: %s" % (RequestHandler.db, str(e)))
                return 

            # Extracts the post data
            form = cgi.FieldStorage(fp=self.rfile, 
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD':'POST',
                                             'CONTENT_TYPE':self.headers['Content-Type'],
                                             })

            self.logger.debug("Received parameters: %s" % str(form))

            # Dispatches the request to the appropriate method
            if self.path == self.submission_path:
                self.submission(form)
                return

            else:
                self.send_error(400, 'Resource not found: %s' % self.sanitize(self.path)) 
                return

            # Never reached
            return
        except Exception, err:
            self.wfile.write("An error occurred: " + self.sanitize(str(err)))
            self.logger.error("An error occurred: " + str(err))
            # Uncomment the following two lines to obtain more complete error information
            if True:
                et, ev, tb = sys.exc_info()
                traceback.print_tb(tb)
            return


def usage(fname):
    print "%s [-d (debug)] [-p <port>] [-b <database>] [-l <log file>] [-i <init file>]" % fname


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv

    debug = False
    port = 8080
    log_level = logging.INFO
    log_file = None
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    RequestHandler.db = "database"
    initialize = False
    team_file = "../../teams.ini"
    services_file = "../../services.ini"

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "idhp:b:l:")
        except getopt.error, msg:
            raise Usage(msg)
        for o, a in opts:
            if o == "-h":
                usage(os.path.basename(argv[0]))
                return 1
            if o == "-d":
                debug = True
            if o == "-p":
                port = int(a)
            if o == "-b":
                RequestHandler.db = a
            if o == "-l":
                log_file = a
            if o == "-t":
                team_file = a
            if o == "-i":
                initialize = True
    except Usage, err:
        logging.error("%s -- for help use -h" % err.msg)
        return 1

    if debug:
        log_level = logging.DEBUG

    # Sets up logging
    logging.basicConfig(level=log_level, filename=log_file, format=log_format)
    logger = logging.getLogger('WebServer')
    RequestHandler.logger = logger


    #load team mappings
    config = ConfigParser.ConfigParser()
    config.read([team_file])
    ip_teams = dict()
    for team in config.sections():
        pfx24 = '.'.join(config.get(team, 'network').split('.')[:-1])
        ip_teams[pfx24] = team
    logging.debug('%r' % ip_teams)
    RequestHandler.ip_teams = ip_teams

    # load service points
    config = ConfigParser.ConfigParser()
    config.read([services_file])
    points = dict()
    for service in config.sections():
        points[service] = int(config.get(service, 'points'))
    logging.debug('%r' % points)
    RequestHandler.points = points


    # If the database needs to be initialized, reads the values from the init file
    if initialize:
        try:
            # Empties the exisiting database
            file = open(RequestHandler.db, "w+")
            file.close()
            conn = sqlite3.connect(RequestHandler.db)
            cur = conn.cursor()
            cur.execute("""create table submitted (team_short_name text, service text, tick text);""")
            cur.execute("""create index whole on submitted (team_short_name, service, tick);""")
            conn.commit()
            cur.close()
        except Exception, err:
            logger.error("Failed to initialize the database: %s" % str(err))
            # Uncomment the following two lines to obtain more complete error information
            if debug:
                et, ev, tb = sys.exc_info()
                traceback.print_tb(tb)
            return 1

    # Makes sure that the database exists
    try:
        RequestHandler.conn= sqlite3.connect(RequestHandler.db)
        cur = RequestHandler.conn.cursor()
        cur.execute("""select count(*) from submitted;""")
        cur.close()
    except Exception, e:
        logger.error("Missing or corrupted database file %s: %s" % (RequestHandler.db, str(e)))
        return 1

    # Starts the web server
    logger.debug("Listening on port %d" % port)
    try:
        logger.info("Starting the web server...")    
        httpd = ThreadingHTTPServer(('', port), RequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down the web server...')
        httpd.socket.close()
    except Exception, e:
       logger.error("Error starting the web server: %s" % str(e))
       return 1

if __name__ == '__main__':
    sys.exit(main())
