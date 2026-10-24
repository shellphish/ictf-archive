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
import Cookie

debug = 1
class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer): pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # A class-level lock to be used for synchronization
    lock = threading.Lock()

    # Paths to the resources
    home_path = "/"
    css_path = "/style.css"
    icon_path = "/favicon.ico"
    icon_file = "favicon.ico"
    login_path = "/login"
    logout_path = "/logout"
    register_path = "/register"
    status_path = "/status"
    send_path = "/send"
    batch_path = "/batch"
    msg_server = "localhost"
    msg_server_port = 31337
    cookie_name = "alertsession"
    # Secret used to generate sessions
    secret = "milkthemule"

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
        <p>[<a href="%s">Register</a>][<a href="%s">Home</a>][<a href="%s">Logout</a>]</p>
      </div>
    </div>
  </body>
</html>
""" % (register_path, home_path, logout_path)

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
  font-family: Courier, fixed;
  font-size: 10pt;
  background: white;
  color: black;
}

#content {
  border: 10px solid orange;
  width: 800px;
  margin-top: 2em;
  margin-left: auto;
  margin-right:auto;
}

#banner {
  padding: 1em 1em 1em 1em;
  border: 0px solid red;
  background: yellow;
  color: black;
  text-align: center;
}

#main {
  padding: 1em 1em 1em 1em;
  border: 10px solid ocre;
}

#footer {
  border: 0px solid yellow;
  font-size: 8pt;
  padding: 1em 1em 1em 1em;
  text-align: center;
}

.username {
  text-decoration: none;
  color: gray;
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

    # Prints the registration page
    def register_page(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Mule Alert Registration", "Mule Alert Registration"))

        self.wfile.write("""
<fieldset>
  <legend>Mule Registration</legend>
  <form action="%s" method="post">
    <p>Username: <input type="text" name="username" /></p>
    <p>Password: <input type="password" name="password" /></p>
    <p><input type="submit" name="submit" value="Register"></p>
  </form>
</fieldset>
""" % self.register_path)
        self.wfile.write(self.footer)
        return

    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Mule Alert", "Mule Alerting System"))

        # Checks if the user is logged in
        session = self.auth()
        
        # The user is not logged in: prints the login form
        if session == None:
            self.wfile.write("""
<fieldset>
  <legend>Mule Login</legend>
  <form action="%s" method="post">
    <p>Username: <input type="text" name="username" /></p>
    <p>Password: <input type="password" name="password" /></p>
    <p><input type="submit" name="submit" value="Login"></p>
  </form>
</fieldset>
""" % self.login_path)
        # The user has a valid session: prints the send message form
        else:
            cur = self.conn.cursor()
            cur.execute("""select username from users where session=?""", (session, ))
            result = cur.fetchone()
            if result == None:
                self.write("There was an error retrieving your data.")
            else:
                username = result[0]
                self.wfile.write("""
<p>Welcome <a class="username" href="%s">%s</a>!</p>
<fieldset>
  <legend>Send a message</legend>
  <form action="%s" method = "post" >
    <p>Group: <input type="text" name="group" /></p>
    <p>Subject: <input type="text" name="subject" /></p>
    <textarea rows="8" cols="80" name="data" /></textarea>
    <p><input type="submit" name="submit" value="Send"></p>
  </form>
</fieldset>                    
""" % (self.status_path, username, self.send_path))
                
        self.wfile.write(self.footer)
        return

    # Prints the home page
    def status(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Mule Alert", "Alert Dispatch Status"))

        # Checks if the user is logged in
        session = self.auth()
        
        # The user is not logged in: prints the login form
        if session == None:
            self.wfile.write("<p>Your are not logged in.</p>")
            self.wfile.write(self.footer)
            return

        try:
            cur = self.conn.cursor()
            cur.execute("""select username, data from users where session='%s'"""  % session)
            result = cur.fetchone()
            if result == None:
                self.wfile.write("""
<p>There was an error retrieving your data.</p>
""")
                self.wfile.write(self.footer)
                return
            self.logger.debug("Received result %s" % str(result));
            username = result[0]
            data = result[1]
            if data == None:
                data = ""
            if len(data) == 0:
                self.wfile.write("""
<p>There is no message history.</p>
""")
                self.wfile.write(self.footer)
                return
            self.logger.debug("Retrieved data: [%s]" % data)
            (timestamp, group, subject, body) = data.split('#')

            self.wfile.write("""
<p>Your last succesfully-sent message was sent on %s:</p>
<p>Group: %s</p>
<p>Subject: %s</p>
<p>Data: %s</p>
""" % (timestamp, group, subject, body))
            self.wfile.write(self.footer)

        except Exception, err:
            self.logger.error("An error occurred: %s" % str (err))
            self.wfile.write("""
<p>An error occurred when processing the message history.</p>
""");
            self.wfile.write(self.footer)
            return
        return


    

    # Registers a new user
    def register(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Registration", "Registration"))

        try:
            username = self.sanitize(form.getfirst("username"))
            password = self.sanitize(form.getfirst("password"))

            self.logger.debug("Requested registration with username [%s] and password [%s]" % (username, password))

            # Checks if the username already exists (note that the check + update must be atomic)
            with RequestHandler.lock:

                cur = self.conn.cursor()
                cur.execute("""select * from users where username=?""", (username, ))

                if cur.fetchone() != None:
                    cur.close()
                    self.wfile.write("""
<p>A user with the selected username already exists. Please choose a different username.</p>
""")
                    self.wfile.write(self.footer)
                    return

                md5 = hashlib.md5()
                md5.update(password)
                password = md5.hexdigest()
                session = "-"
                cur.execute("""insert into users (username, password, session) values (?,?,?);""", (username, password, session))
                self.conn.commit()
                cur.close()
                self.wfile.write("""
<p>User successfully registered.</p>
""")
                self.wfile.write(self.footer)
        except Exception, err:
            self.logger.error("An error occurred when registering your account: %s" % str (err))
            self.wfile.write(self.footer)
            return
        return

    # Batch registration
    def batch(self, form):
        self.wfile.write(self.header % ("Batch Registration", "Batch Registration"))
        self.wfile.write("To be implemented")
        self.wfile.write(self.footer)

    def auth(self):
        cookie = self.headers.getheaders('Cookie')
        if cookie == None or len(cookie) == 0:
            return None
        try:
            session = None
            morsels = cookie[0].split(";");
            self.logger.debug("Received cookie: %s" % str(morsels))
            for m in morsels:
                (var, val) = m.strip().split('=')
                if var == self.cookie_name:
                    session = val
                    break;
        except Exception, err:
            self.logger.debug("Error in parsing cookie %s: %s" % (cookie, str(err)))
            return None
        self.logger.debug("Setting session to: %s" % session)
       
        cur = self.conn.cursor()
        cur.execute("""select * from users where session=?""", (session, ))
        if cur.fetchone() == None:
            cur.close()
            return None
        cur.close()
        return session
        
    # Login 
    def login(self, form):
        try:
            username = self.sanitize(form.getfirst("username"))
            password = self.sanitize(form.getfirst("password"))

            self.logger.debug("Requested login with username [%s] and password [%s]" % (username, password))
            md5 = hashlib.md5()
            md5.update(password)
            password = md5.hexdigest()

            cur = self.conn.cursor()
            cur.execute("""select * from users where username=? and password=?""", (username, password))

            if username == "" or password == "" or cur.fetchone() == None:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.header % ("Login", "Invalid Login"))
                self.wfile.write("""
<p>Authentication failed. Please check that the provided username/password combination is correct.</p>
""")
                self.wfile.write(self.footer)
                self.logger.error("Invalid login with username [%s] and password [%s]" % (username, password))
                cur.close()
                return

            # Computes the session token, if one is not already set
            session = self.auth()
            if session == None or session == "" or session == "-" or session == "None":
                cookie = self.headers.getheaders('Cookie')
                if cookie != None and len(cookie) != 0:
                    session = None
                    morsels = cookie[0].split(";");
                    self.logger.debug("Parsed cookie: %s" % str(morsels))
                    for m in morsels:
                        (var, val) = m.strip().split('=')
                        if var == self.cookie_name:
                            session = val
                            break;
                else:
                    self.logger.debug("Session is missing, creating one (%s)" % str(session)) 
                    md5 = hashlib.md5()
                    md5.update(str(time.time()) + username + password + self.secret)
                    session = md5.hexdigest()

            # Updates the database
            with RequestHandler.lock:
                self.logger.debug("Setting the motherfucking session to %s" % session)
                cur.execute("""update users set session=? where username=? and password=?""", (session, username, password))
                self.conn.commit()
                cur.close()
        except Exception, err:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write("""ERROR: An error occurred while processing your login: %s""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            cur.close()
            self.logger.error("An error occurred in processing the login: %s" % str(err))
            return
                         
        # Success: redirects the user to the home page and sets the cookie
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '%s' % self.home_path)
        self.send_header('Set-Cookie', "%s=%s" % (self.cookie_name, session))
        self.end_headers()
        return

    def send(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Send Alert", "Send Alert"))

        try:
            session = self.auth()

            # If there is no session, redirect to home page
            if session == None:
                self.wfile.write("<p>Your are not logged in.</p>")
                self.wfile.write(self.footer)
                return

            cur = self.conn.cursor()
            cur.execute("""select username from users where session=?""", (session, ))
            result = cur.fetchone()
            if result == None:
                self.wfile.write("""
<p>There was an error retrieving your session.</p>
""")
                self.wfile.write(self.footer)
                return

            username = result[0]

            group = self.sanitize(form.getfirst("group"))
            subject = self.sanitize(form.getfirst("subject"))
            body = self.sanitize(form.getfirst("data"))
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.logger.debug("Requested alert message [%s:%s] for group [%s] on %s" % (subject, body, group, timestamp))
            data = "%s#%s#%s#%s" % (timestamp, group, subject, body)
            self.logger.debug("Setting user data to %s with session %s" % (data, session))
            with RequestHandler.lock:
                cur.execute("""update users set data = ? where session = ?""", (data, session))
                self.conn.commit()
                cur.close()
            self.wfile.write("""
<p class="log_msg">Contacting message dispatcher...</p>
""");
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.msg_server, self.msg_server_port))
            infd = s.makefile()

            msg ="""SEND %s .oOo.
<msg>
  <time>%s</time>
  <sender>%s</sender>
  <group>%s</group>
  <subject>%s</subject>
  <msgbody>%s</msgbody>
</msg>
.oOo.
""" % (username, timestamp, username, group, subject, body)
            self.wfile.write("""
<p class="log_msg">Sending message...</p>
""");
            s.send(msg)
            self.logger.debug("Message sent, waiting for answer")
            self.wfile.write("""
<p class="log_msg">Message sent...</p>
""");
            response = infd.readline()
            self.wfile.write("""
<p class="log_msg">Received response: %s...</p>
""" % response);
            
        except Exception, err:
            self.logger.error("An error occurred when sending the alert: %s" % str (err))
            self.wfile.write("""
<p class="log_msg">There was an error: %s...</p>
""" % str(err));
            self.wfile.write(self.footer)
            return

        self.wfile.write(self.footer)
        return


    # Logout
    def logout(self, params):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(self.header % ("Logout", "Logout"))

            session = self.auth()

            if session == None:
                self.wfile.write("<p>Your are not logged in.</p>")
                self.wfile.write(self.footer)
                return

            cur = self.conn.cursor()
            with RequestHandler.lock:
                cur.execute("""update users set session='-' where session=?""", (session, ))
                self.conn.commit()
                cur.close()
        except Exception, err:
            self.wfile.write("""ERROR: An error occurred while logging you out: %s""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            cur.close()
            self.logger.error("An error occurred in processing the logout: %s" % str(err))
            return
                         
        self.wfile.write("""
<p>You have been logged out.</p>
""")
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

            elif req.path == self.register_path:
                self.register_page(params)
                return

            elif req.path == self.status_path:
                self.status(params)
                return

            elif req.path == self.logout_path:
                self.logout(params)
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
            if self.path == self.login_path:
                self.login(form)
                return

            elif self.path == self.register_path:
                self.register(form)
                return

            elif self.path == self.send_path:
                self.send(form)
                return

            elif self.path == self.batch_path:
                self.batch(form)
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
    port = 11111
    log_level = logging.INFO
    log_file = None
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    RequestHandler.db = "/home/sendalert/database"
    initialize = False
    init_file = None

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
    logger = logging.getLogger('SendAlert')
    RequestHandler.logger = logger

    # If the database needs to be initialized, reads the values from the init file
    if initialize:
        try:
            # Empties the exisiting database
            file = open(RequestHandler.db, "w+")
            file.close()
            conn = sqlite3.connect(RequestHandler.db)
            cur = conn.cursor()
            cur.execute("""create table users (username text, password text, data text, session text);""")
            config = ConfigParser.ConfigParser()
            config.read(init_file)

            for username in config.sections():
                try:
                    password = config.get(username, "password")
                    md5 = hashlib.md5()
                    md5.update(password)
                    password = md5.hexdigest()
                    data = config.get(username, "data")
                    session = "-"
                    cur.execute("""insert into users (username, password, data, session) values (?,?,?,?);""",
                                 (username, password, data, session))
                except Exception, e:
                    logger.error("Error while parsing init file: %s" % str(e))
                    raise
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
        cur.execute("""select * from users;""")
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

def start():
    sys.exit(main())
