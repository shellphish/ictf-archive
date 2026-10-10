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
import time
import ConfigParser
import SocketServer
import threading

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer): pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # A class-level lock to be used for synchronization
    lock = threading.Lock()

    # Paths to the resources
    home_path = "/"
    bribe_path = "/bribe"
    css_path = "/style.css"
    icon_path = "/favicon.ico"
    icon_file = "webserver.ico"

    # Parameters for accessing the database dump
    dump_auth_attr = "auth"
    dump_auth_value = "s3cr3t"

    # Secret used to generate sessions
    secret = "youwillneverguessthissecretphrase"
    credentials = "iseeeverything"

    minute_value_file = 'minute_value_file'

    #http://scorekeeper/bribes?team=<team name>&credentials=iseeeverything&money=<bribe amount>
    bribe_request = 'http://scorekeeper/bribes?'
    #bribe_request = 'http://localhost:8082/bribes?'
    #firewall_request = 'http://192.168.48.35:8081/rules?'
    firewall_request = 'http://nop:8081/rules?'

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
        <p>[<a href='""" + home_path + """'>Bribe</a>]</p>
      </div>
    </div>
  </body>
</html>
"""

    # Sanitizes input from the user
    def sanitize(self, string):
        allowed = "0123456789"
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
  font-family: arial, sans-serif;
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
  text-align: center;
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

    def cur_minute_value (self):
      return int(open(self.minute_value_file, 'r').read().strip())

    def ip_to_team (self, ip):
      pfx24 = '.'.join(ip.split('.')[:-1])
      if pfx24 in self.ip_teams:
        return self.ip_teams[pfx24]
      else:
        return None

    def get_form_cookie(self):
        md5 = hashlib.md5()
        md5.update(self.client_address[0] + self.secret)
        return md5.hexdigest()

    def verify_form_cookie(self, cookie):
        valid = self.get_form_cookie()
        return valid == cookie

    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.header % ("Bribe", "Bribe Them (c) by ziemenz"))
        self.wfile.write("""
<form action=/bribe method="GET" class="center">
How much do you want to invest?<br/><br/>
Your current exchangerate should be around %i per minute<br/><br/>
<input type=text value="100" name="bribe" width="100px"/><br/><br/>
<input type=hidden value="%s" name="fc">
<input type=Submit value="Bribe"/>
</form>
""" % (self.cur_minute_value(), self.get_form_cookie()))
        self.wfile.write(self.footer)
        return

    # Prints the bribe page
    def bribe(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.header % ("Bribe", "Bribe Them (c) by ziemenz"))

        if 'fc' not in params or not self.verify_form_cookie(params['fc'][0]):
          self.wfile.write("""Go Away!""")
          self.wfile.write(self.footer)
          return

        minute_value = self.cur_minute_value()
        if not minute_value:
          minute_value = 100
        bribe = 0
        if params.has_key('bribe'):
          try:
            bribe = int(params['bribe'][0])
          except Exception, e:
            pass
        self.wfile.write("""Exchange rate is: %i you spent %i <br>""" % (minute_value, bribe))
        trans = False
        team = None
        minutes = 0

        # no negative bribes
        if bribe > 0:
          minutes = int(bribe / minute_value)

          # only pay bribes that are above 1 time unit 
          if minutes > 0:
            brq = self.bribe_request
            client_ip = self.client_address[0]

            # check whether we can identify the team
            team = self.ip_to_team(client_ip)
            if team:
              #perform transaction
              brq += urllib.urlencode({"team" : team, "credentials" : self.credentials, "money" : bribe})
              self.logger.debug('Sending request to scorekeeper: %s' % brq)
              try:
                res = urllib.urlopen(brq).read()
                if res == 'SUCCESS\n':
                  trans = True
              except Exception, e:
                self.logger.info('Scorekeeper request failed: %s' % e)
          else:
            self.wfile.write("""<p>Try to bribe somebody else with these peanuts!</p>""")
        if trans and minutes and team:
          #signal the firewall
          frq = self.firewall_request
          frq += urllib.urlencode({"team" : team, "howlong" : minutes * 60, "action" : "unblock"})
          self.logger.debug('Sending request to firewall: %s' % frq)
          try:
            res = urllib.urlopen(frq).read()
            self.wfile.write("""Your bribe has been forwarded to the administrators [%i]<br/>""" % (minutes))
            self.wfile.write(res)
          except Exception, e:
            self.logger.info("Firewall request failed %s" % e)
            self.wfile.write("""An error occured""")
        else:
          self.wfile.write('Transaction Aborted')
        self.wfile.write(self.footer)
        return

    def do_GET(self):
        try:
            self.logger.debug("Received GET request with path: %s" %  self.path)

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

            elif req.path == self.bribe_path:
                self.bribe(params)
                return

            elif req.path == self.css_path:
                self.style(params)
                return

            elif req.path == self.icon_path:
                self.icon(params)
                return

            else:
                self.send_error(404,'Resource Not Found: %s' % self.sanitize(self.path))                
                return
            # Never reached
            return
        except Exception, err:
            self.wfile.write("An error occurred: " + self.sanitize(str(err)))
            self.logger.error("An error occurred: " + str(err))
            if True:
                et, ev, tb = sys.exc_info()
                traceback.print_tb(tb)
            return


def usage(fname):
    print "%s [-d (debug)] [-p <port>] [-l <log file>] [-i <init file>]" % fname


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv

    debug = False
    port = 8082
    log_level = logging.INFO
    log_file = None
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    RequestHandler.db = "database"
    initialize = False
    init_file = 'teams.ini'

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "dhp:b:l:i:")
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
            if o == "-i":
                initialize = True 
                init_file = a

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
    config.read([init_file])
    ip_teams = dict()
    for team in config.sections():
      pfx24 = '.'.join(config.get(team, 'network').split('.')[:-1])
      ip_teams[pfx24] = team
    #print '%r' % ip_teams
    RequestHandler.ip_teams = ip_teams

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
