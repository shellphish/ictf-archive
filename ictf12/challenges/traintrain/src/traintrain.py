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
import re

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer): pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # A class-level lock to be used for synchronization
    lock = threading.Lock()

    # Paths to the resources
    home_path = "/"
    css_path = "/style.css"
    icon_path = "/favicon.ico"
    icon_file = "traintrain.ico"
    background_path = "/background.jpg"
    background_file = "traintrain.jpg"
    login_path = "/login"
    logout_path = "/logout"
    register_path = "/register"
    solution_path = "/solution"
    manual_path = "/manual"
    dump_path = "/dump"
    assignment_file_re = re.compile("/assignment_[0-9a-f]+\.ass")
    assignment_dir = "/tmp"
    # Parameters for accessing the database dump
    dump_allowed = False
    dump_auth_attr = "auth"
    dump_auth_value = "s3cr3t"



    # Secret used to generate sessions
    secret = "trainingthetrainintherain"

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
        <p>[<a href='""" + home_path + """'>Home</a>][<a href='""" + logout_path + """'>Logout</a>]</p>
      </div>
    </div>
  </body>
</html>
"""

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

    # Sanitizes input from the user
    def shell_sanitize(self, string):
        allowed = " '.,:!?()-/_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if string == None:
            return ""
        newstring = ""
        for c in string:
            if c in allowed:
                newstring = newstring + c
        return newstring

    # Returns the CSS style file
    def background(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'image/jpg')
        self.end_headers()

        try:
            data = open(self.background_file, "r").read()
            self.wfile.write(data)
        except Exception, err:
            self.logger.error("Cannot access background image: %s" % str(err))
            return 1
        return 0

    # Returns the CSS style file
    def style(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()

        self.wfile.write("""
body {
  font-family: courier, fixed;
  font-size: 12pt;
  background: white;
  color: black;
}

#content {
  background: white;
  border: 4px solid #CFCFCF;
  width: 1200px;
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

#image_container {
}

#image {
  padding: 1em 1em 1em 1em;
  border: 0px solid blue;
  width: 400px;
}

#similar_users {
    width: 800px;
    border: 1px solid #CFCFCF;
}
    
#footer {
  border: 0px solid yellow;
  font-size: 12pt;
  padding: 1em 1em 1em 1em;
  text-align: center;
}
""")
        return

    # Updates a user history
    def history(self, session, path):
        ret_val = 0
        if path == self.css_path:
            return ret_val
        if path == self.dump_path:
            return ret_val
        
        self.logger.debug("Adding to history: %s" % path)
        with RequestHandler.lock:
            try:
                cur = self.conn.cursor()
                cur.execute("select history from users where session=?", (session,))
                
                result = cur.fetchone()
                if result == None:
                    self.write("There was an error retrieving your data.")
                    ret_val = 1
                else:
                    self.logger.debug("Retrieved history: %s" % result[0])
                    if result[0] == None:
                        prev_history = ""
                    else:
                        prev_history = result[0] + ":"
                    history = prev_history + urllib2.unquote(path)
                    self.logger.debug("New history: %s" % history)
                    
                    cur.execute("update users set history=? where session=?", (history, session))
                    self.conn.commit()
            except Exception, err:
                self.logger.error("Cannot update history: %s" % str(err))
                ret_val = 1 
        return ret_val

        
    # Returns the favicon.ico icon
    def icon(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'image/vnd.microsoft.icon')
        self.end_headers()

        try:
            f = open(self.icon_file, "r")
            self.wfile.write(f.read())
            f.close()
        except Exception, err:
            self.logger.debug("Cannot open icon: %s" % str(err))


    # Prints the home page
    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("TrainTrain", "TrainTrain"))

        # Checks if the user is logged in
        session = self.auth()
        
        # The user is not logged in: prints the login and registration forms
        if session == None:
            self.wfile.write("""
<table>
<tr>
<td>
<p>Welcome to the Train Transportation Training System (TrainTrain).<p>
<p>This application is only for Transportation Trainees (TTs).</p>
<p>If you are not a TT, please click <a href="https://www.google.com/search?q=train+crashes">here</a>.</p>
<p>Note that the Training System is directly connected to the actual training system, so try not to screw up.</p>
<p>For this reason, we track all activity on the site. Be forewarned!</p>
<hr />
<p>If you already have an account please log in using the form below.</p>

<fieldset>
  <legend>Login</legend>
  <form name="login" action="%s" method="post">
    <p>Username: <input type="text" name="username" /></p>
    <p>Password: <input type="password" name="password" /></p>
    <p><input type="submit" name="submit" value="Login"></p>
  </form>
</fieldset>
<p>If you do not have an account, please register using the form below. Note that you need to provide an authorization key that you must obtain from your Train System Trainer</p>
<fieldset>
  <legend>Register</legend>
  <form name="register" action="%s" method="post">
    <p>Username: <input type="text" name="username" /></p>
    <p>Password: <input type="password" name="password" /></p>
    <p>Authorization: <input type="text" name="authorization" /></p>
    <p><input type="submit" name="submit" value="Register"></p>
  </form>
</fieldset>
</td>
<td>
<div id="image_container"><img id="image" src="background.jpg" /></div>
</td>
</tr>
</table>
""" % (self.login_path, self.register_path))
        # The user has a valid session: prints his/her data
        else:
            cur = self.conn.cursor()
            cur.execute("""select * from users where session=?""", (session, ))
            result = cur.fetchone()
            if result == None:
                self.write("There was an error retrieving your data.")
            else:
                username = result[0]
                password = result[1]
                authorization = result[2]
                session = result[3]
                self.wfile.write("""
<p>Welcome %s, your authorization data is:</p>
<pre>
%s
</pre>""" % (username, authorization))
                md5 = hashlib.md5()
                md5.update(str(time.mktime(time.gmtime())) + str(os.getpid()) + self.secret)
                assignment  = md5.hexdigest()
                
                assignment_file = "assignment_%s.ass" % (assignment,)
                assignment_path = "%s/%s" % (self.assignment_dir, assignment_file)
                os.system("python ./generate_assignment -o %s" % assignment_path)
                self.wfile.write("""
<p>Your assignment can be downloaded <a href="%s">here</a>""" % assignment_file)
                self.wfile.write("""
<p>Please submit the solution to your training assignment for scoring: </p>
<fieldset>
  <legend>Assignment Solution</legend>
  <form name="solution" action="%s" method="post">
    <p>Solution: <input type="text" name="solution" /></p>
    <p><input type="hidden" name="assignment" value="%s" /></p>
    <p><input type="submit" name="submit" value="Submit" /></p>
  </form>
</fieldset>
""" % (self.solution_path, assignment))
        
        self.wfile.write(self.footer)
        return

    def manual(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Dumps the database
        self.wfile.write(self.header % ("The Manual", "The Manual"))

        self.wfile.write(""" 
<p>This is supposedly some meaningful documentation.</p>
        """)
        
        self.wfile.write(self.footer)
        return
        
    def dump(self, params):
        if not self.dump_allowed:
            return
        
        
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
        self.wfile.write(self.header % ("The Database", "The Database"))

        cur = self.conn.cursor()
        cur.execute("""select username, password, authorization, session, history, score, solution from users""")
        for row in cur:
            self.wfile.write("""
<pre>
%s
    password: %s
    authorization: %s
    session: %s
    history: %s
    score: %s
    solution: %s
</pre>""" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        cur.close()

        
        self.wfile.write(self.footer)
        return


    def auth(self):
        cookies = self.headers.getheaders('Cookie')
        if cookies == None or len(cookies) == 0:
            return None
        self.logger.debug("Received cookies: %s"% str(cookies))
        for cookie in cookies:
            try:
                attr_vals = cookie.split(';')
                for attr_val in attr_vals:
                    self.logger.debug("Considering attribute/value pair: %s"% str(attr_val))
                    attribute, value = attr_val.split('=')
                    if attribute == "session":
                        session = value
                        break
            except Exception, err:
                self.logger.debug("Error in parsing cookie %s: %s" % (str(cookie), str(err)))
                return None
        with RequestHandler.lock:
            cur = self.conn.cursor()
            cur.execute("""select * from users where session=?""", (session, ))
            if cur.fetchone() == None:
                cur.close()
                return None
            cur.close()
        return session

        
    # Regsters a new user
    def register(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % ("Registration", "Registration"))

        try:
            username = self.sanitize(form.getfirst("username"))
            password = self.sanitize(form.getfirst("password"))
            authorization = self.sanitize(form.getfirst("authorization"))

            if username == "" or password == "" or authorization == "":
                raise Exception("empty parameter(s)")
                
            self.logger.debug("Requested registration with username [%s], password [%s], and authorization [%s]" % (username, password, authorization))

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
                cur.execute("""insert into users (username, password, authorization) values (?,?,?);""", (username, 
                                                                                                          password, 
                                                                                                          authorization))
                self.conn.commit()
                cur.close()
                self.wfile.write("""
<p>User successfully registered.</p>
""")
                self.wfile.write(self.footer)
        except Exception, err:
            self.logger.error("An error occurred when registering your account: %s" % str (err))
            self.wfile.write("""
<p>User registeration failed: %s.</p>
""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            return
        return


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

            # Computes the session token
            md5 = hashlib.md5()
            md5.update(str(time.time()) + username + password + self.secret)
            session = md5.hexdigest()

            # Updates the database
            with RequestHandler.lock:
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
        self.send_header('Set-Cookie', "session=%s" % session)
        self.end_headers()
        return

    # Submits a solution
    def solution(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write(self.header % ("Evaluation", "Evaluation"))
        # Checks if the user is logged in
        session = self.auth()
        
        # The user is not logged in: prints the login and registration forms
        if session == None:
            self.wfile.write("<p>You are not logged in.</p>")
            self.wfile.write(self.footer)
            return

        try:
            solution = self.shell_sanitize(form.getfirst("solution"))
            assignment = self.shell_sanitize(form.getfirst("assignment"))
            
            self.logger.debug("Submitted solution %s for assignment %s" % (solution, assignment))

            assignment_path = "%s/assignment_%s.ass" % (self.assignment_dir, assignment)
            
            # Evaluates the solution
            command = """python ./evaluate_assignment -i %s -s "%s" """ % (assignment_path, solution)
            self.logger.debug("Executing: %s" % command)
            result = int(os.system(command) / 256)
            self.logger.debug("Returned value is %d" % result)
            if result == 0:
                self.wfile.write("<p>Your solution is incorrect.</p>")
                self.wfile.write(self.footer)
                return
            else:
                self.wfile.write("<p>Your solution is correct: you received %d points</p>" % result)
                
            # Updates the score of the user
            with RequestHandler.lock:

                cur = self.conn.cursor()
                cur.execute("""select score from users where session=?""", (session, ))

                score = cur.fetchone() 
                if score[0] == None:
                    score = 0
                else:
                    score = score[0]
                score = score + result
                cur.execute("update users set score=?, solution=? where session=?", (score, solution, session))
                self.conn.commit()
                
                cur.execute("select history from users where session=?", (session,))
                history = cur.fetchone()
                if history == None:
                    cur.close()
                    return None
                else:
                    history = history[0]
                query = """select username, score from users where history LIKE '%%%s%%' and not session='%s'""" % (history, session)
                self.logger.debug("Executing LIKE query: %s" % query)
                cur.execute(query)
                
                self.wfile.write("""
<p>These are other users who have your same navigation patterns.</p>
<table id="similar_users">
<tr><td>username</td><td>score</td></tr>""")
                for row in cur:
                    self.wfile.write("""
<tr><td>%s</td><td>%s</td></tr>""" % (row[0], row[1]))
                self.wfile.write("""
</table>""")
                
                cur.close()
                self.wfile.write("""
<p>Score successfully updated. It is now: %d</p>
""" % score)
                
                self.wfile.write(self.footer)
        except Exception, err:
            self.logger.error("An error occurred when updating your score: %s" % str (err))
            return
        return
    
    # File retrieval
    def file(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
            
        try:
            self.logger.debug("Returning file %s" % params)
            rfile = open(params, "r")
            data = rfile.read()
            rfile.close()
            self.wfile.write(data)
        except Exception, err:
            self.logger.error("An error occurred when returning the file: %s" % str (err))
            return
        
        return
    
    # Logout
    def logout(self, params):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(self.header % ("Logout", "Logout"))

            session = self.auth()

            # If there is no session, redirect to home page
            if session == None:
                self.wfile.write("<p>You are not logged in.</p>")
                self.wfile.write(self.footer)
                return

            cur = self.conn.cursor()
            cur.execute("""select * from users where session=?""", (session, ))
            result = cur.fetchone()
            if result == None:
                self.wfile.write("""
<p>There was an error retrieving your session.</p>
""")
                self.wfile.write(self.footer)
                return

            username = result[0]
            password = result[1]
            data = result[2]
            session = result[3]

            # Updates the database
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
            
            # If session is enabled save path
            session = self.auth()
        
            # The user is logged in, adds the path to the history
            if session != None:
                self.logger.debug("Updating navigation history with %s" % req.path)
                self.history(session, req.path) 

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

            elif req.path == self.background_path:
                self.background(params)
                return
            
            elif req.path == self.icon_path:
                self.icon(params)
                return

            elif req.path == self.dump_path:
                self.dump(params)
                return
            
            elif req.path == self.manual_path:
                self.manual(params)
                return

            elif req.path == self.logout_path:
                self.logout(params)
                return
            
            elif self.assignment_file_re.match(req.path):
                self.file("%s%s" % (self.assignment_dir, req.path)) 
                return
               
            else:
                self.send_error(404,'Resource Not Found: %s' % self.sanitize(self.path))                
                return
            # Never reached
            return
        except Exception, err:
            self.wfile.write("An error occurred: " + self.sanitize(str(err)))
            self.logger.error("An error occurred: " + str(err))
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

            # Parses the request
            req = urlparse.urlparse(self.path)
            self.logger.debug("Received request resource: %s" % req.path)
            
            # If session is enabled save path
            session = self.auth()
        
            # The user is logged in, adds the path to the history
            if session != None:
                self.logger.debug("Updating navigation history with %s" % req.path)
                self.history(session, req.path) 

            # Extracts the post data
            form = cgi.FieldStorage(fp=self.rfile, 
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD':'POST',
                                             'CONTENT_TYPE':self.headers['Content-Type'],
                                             })

            self.logger.debug("Received parameters: %s" % str(form))

            # Dispatches the request to the appropriate method
            if req.path == self.login_path:
                self.login(form)
                return

            elif req.path == self.register_path:
                self.register(form)
                return
            
            elif req.path == self.solution_path:
                self.solution(form)
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
            #et, ev, tb = sys.exc_info()
            #traceback.print_tb(tb)
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
    port = 8888
    log_level = logging.INFO
    log_file = None
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    RequestHandler.db = "traintrain.db"
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
    logger = logging.getLogger('TrainTrain')
    RequestHandler.logger = logger

    # If the database needs to be initialized, reads the values from the init file
    if initialize:
        try:
            # Empties the exisiting database
            file = open(RequestHandler.db, "w+")
            file.close()
            conn = sqlite3.connect(RequestHandler.db)
            cur = conn.cursor()
            cur.execute("""create table users (username text, password text, authorization text, session text, history text, score int, assignment text, solution text);""")
            config = ConfigParser.ConfigParser()
            config.read(init_file)
            for username in config.sections():
                try:
                    password = config.get(username, "password")
                    authorization = config.get(username, "authorization")
                    md5 = hashlib.md5()
                    md5.update(password)
                    password = md5.hexdigest()
                    cur.execute("""insert into users ('username', 'password', 'authorization') values (?,?,?);""", (username, 
                                                                                                                    password, 
                                                                                                                    authorization))
                except Exception, e:
                    logger.error("Error while parsing init file %s: %s" % (init_file, str(e)))
                    raise
            conn.commit()
            cur.close()
        except Exception, err:
            logger.error("Failed to initialize the database: %s" % str(err))
            et, ev, tb = sys.exc_info()
            traceback.print_tb(tb)
            return 1
        
        # Initialization succeeded. Terminate.
        return 0

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
        logger.info("Starting TrainTrain...")    
        httpd = ThreadingHTTPServer(('', port), RequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down TrainTrain...')
        httpd.socket.close()
    except Exception, e:
       logger.error("Error starting TrainTrain: %s" % str(e))
       return 1

if __name__ == '__main__':
    sys.exit(main())
