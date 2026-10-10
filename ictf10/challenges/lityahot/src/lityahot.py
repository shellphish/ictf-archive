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

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer): pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # A class-level lock to be used for synchronization
    lock = threading.Lock()

    # Paths to the resources
    home_path = "/"
    css_path = "/style.css"
    icon_path = "/favicon.ico"
    icon_file = "lityahot.png"
    banner_file = "/home/seclab/lityahot_banner.png"
    banner_path = "/banner"
    update_path = "/update"
    dump_path = "/dump"

    # Parameters for accessing the database dump
    dump_auth_attr = "auth"
    dump_auth_value = "s3cr3t"

    # Secret used to generate sessions
    secret = "youwillneverguessthissecretphrase"

    # Header and footer

    # Sanitizes input from the user
    def sanitize(self, string):
	allowed = " &=:/'.,_ !?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
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
  color: white;
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


    def banner(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'image/JPEG')
        self.end_headers()

        try:
            f = open(self.banner_file, "r")
            self.wfile.write(f.read())
        except Exception, err:
            self.logger.debug("Cannot open banner: %s" % str(err))

    # Prints the home page
    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write("""<body bgcolor="pink">""")

	self.wfile.write("""
<table align="center">
<tr>
<td align="center"><img src="banner"></td>
</tr>
</table>
	""")


	self.wfile.write("""
<h2 align="justify">Do you dream of a job in Litya's television? Would you like to participate to one of our awesome reality shows? Apply now by sending us your pictures! If we like you, we will get back to you soon! And since we believe that if you are pretty you must also be smart, a bright career in politics might be waiting for you!</h2>
<p>(Remember that, on paper, you must be 18 or older to apply.)</p>
	""")
        
	self.wfile.write("""
<fieldset>
  <legend>Send us your pictures!</legend>
  <form action="%s" method="post">
    <p>Your Name: <br><input type="text" name="name" /></p>
    <p>Link to your pictures: <br><input type="url" name="url" /></p>
    <p>Comments: <br><textarea name="comment" COLS=40 ROWS=6></textarea></p>
    <p><input type="submit" name="submit" value="Submit"></p>
  </form>
</fieldset>
<table>
""" % (self.update_path))
        cur = self.conn.cursor() 
	cur.execute("select * from applications;")
	for application in cur.fetchall():
	  name = application[0]
	  url = application[1].startswith("http://") and application[1] or "http://"+application[1]
	  comment = application[2]
          self.wfile.write("""
<tr><td><b>Name: </b>%s<br><br><td></tr>
<tr><td><a href="%s">View %s's pictures</a><br><br><td></tr>
<tr><td><b>Comments: </b>%s<br><hr><td></tr>
"""%(name,url,name,comment))
	self.wfile.write("""</table></body>""")
	
	return


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
        self.wfile.write("""
<table summary="db">
  <thead>
    <tr><td>username</td><td>password</td><td>data</td><td>session</td></tr>
  </thead>
  <tbody>
""")        

        cur = self.conn.cursor()
        cur.execute("""select * from users""")
        for row in cur:
            self.wfile.write("    <tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2], row[3]))
        cur.close()

        self.wfile.write("""
  </tbody>
</table>
""")
        return

    def update(self, form):
      
      name = self.sanitize(form.getfirst("name"))
      url = self.sanitize(form.getfirst("url"))
      comment = self.sanitize(form.getfirst("comment"))

      conn = sqlite3.connect(RequestHandler.db)
      cur = conn.cursor()
      cur.execute("""insert into applications (name,link,comment) values ("%s","%s","%s");"""%(name,url,comment))
      conn.commit()
      cur.close()
      self.home({})
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

	    elif req.path == self.update_path:
	      self.update(params)
	      return
	    
	    elif req.path == self.banner_path:
	      self.banner(params)
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
	    
	    if self.path == self.update_path:
	      self.update(form)
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
            if debug:
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
    init_file = None

    initialize = True

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

    # If the database needs to be initialized, reads the values from the init file
    if initialize:
        try:
            # Empties the exisiting database
            file = open(RequestHandler.db, "w+")
            file.close()
            conn = sqlite3.connect(RequestHandler.db)
            cur = conn.cursor()
            cur.execute("""create table applications (name text, link text, comment text);""")
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
        cur.execute("""select * from applications;""")
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
