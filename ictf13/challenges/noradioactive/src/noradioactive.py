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
import pycassa
import time
import ConfigParser
import SocketServer
import threading
import re

#HOME_STRING = "Home"
HOME_STRING = "Nyumbani"
#REGISTER_STRING = "Register"
REGISTER_STRING = "Kusajili"
#DOCUMENTATION_STRING = "Manual"
DOCUMENTATION_STRING = "Nwongozo"
#LOGOUT_STRING = "Logout"
LOGOUT_STRING = "Ingia nje"
#TITLE_STRING = "Radioactivity Tracking System"
TITLE_STRING = "Mfumo Wa Mionzi Ya Kufuatilia"
#INTRO_STRING = "This is the system to track your radioactive levels"
INTRO_STRING = "Hii ni mfumo wa kufuatilia yako ngazi ya mionzi"
#LOGIN_STRING = "Please log in using the form below"
LOGIN_STRING = "Tafadhali kuingia katika kutumia fomu ya chini"
#LOGIN_FIELDSET_STRING = "Login"
LOGIN_FIELDSET_STRING = "Kuingia"
#USERNAME_FIELD_STRING = "Username"
USERNAME_FIELD_STRING = "Jina la mtumiaji"
#PASSWORD_FIELD_STRING = "Password"
PASSWORD_FIELD_STRING = "Neno siri"
#LOGIN_SUBMIT_STRING = "Submit"
LOGIN_SUBMIT_STRING = "Kuwasilisha"
#WELCOME_STRING = "Welcome"
WELCOME_STRING = "Karibu"
#SERIAL_STRING = "Serial"
SERIAL_STRING = "Idadi"
#SUBMIT_READING_STRING = "Please submit a new radioactivity reading"
SUBMIT_READING_STRING = "Tafadhali kuwasilisha mpya mionzi kusoma"
#FIELDSET_READING_STRING = "Reading"
FIELDSET_READING_STRING = "Kusoma"
#RADIO_FIELD_STRING = "Radioactivity"
RADIO_FIELD_STRING = "Mionzi"
#LOCATION_FIELD_STRING = "Location"
LOCATION_FIELD_STRING = "Eneo"
#READING_SUBMIT_STRING = "Record"
READING_SUBMIT_STRING = "Rekodi"
#REGISTER_STRING = "Register"
REGISTER_STRING = "Kusajili"
#SERIAL_FIELD_STRING = "Serial number"
SERIAL_FIELD_STRING = "Idadi serial"
#REGISTER_SUBMIT_STRING = "Submit"
REGISTER_SUBMIT_STRING = "Kuwasilisha"
#DATABASE_STRING = "The Database"
DATABASE_STRING = "Msingi wa data"
#DATA_STRING = "The Data"
DATA_STRING = "Takwimu"
#SESSIONS_STRING = "The Sessions"
SESSIONS_STRING = "Vikao vya"
#MANUAL_STRING = "The Manual"
MANUAL_STRING = "Nyaraka"
#MANUAL_DATA_STRING = "This application is used to keep track of the levels of radioactivity at various locations."
MANUAL_DATA_STRING = "Maombi haya ni kutumika kwa kuweka wimbo wa ngazi ya mionzi katika maeneo mbalimbali."
#RECORD_READING_STRING = "Record Reading"
RECORD_READING_STRING = "Rekodi Soma"
#NOT_LOGGED_STRING = "You are not logged in."
NOT_LOGGED_STRING = "Wewe si ndani ya."
#READING_RECORDED_STRING = "Reading successfully recorded."
READING_RECORDED_STRING = "Kusoma mafanikio kumbukumbu."
#COLOCATED_WORKERS_STRING = "Colocated workers"
COLOCATED_WORKERS_STRING = "sawa wafanyakazi mahali"
#REGISTRATION_STRING = "Registration"
REGISTRATION_STRING = "Usajili"
#USER_REGISTERED_STRING = "User successfully registered."
USER_REGISTERED_STRING = "Mtumiaji mafanikio aliongeza."
#USER_REGISTRATION_FAILED_STRING = "User registeration failed"
USER_REGISTRATION_FAILED_STRING = "Mtumiaji registeration kushindwa"
#AUTHENTICATION_FAILED_STRING = "Authentication failed. Please check that the provided username/password combination is correct."
AUTHENTICATION_FAILED_STRING = "Uthibitisho alishindwa. Tafadhali angalia kwamba zinazotolewa jina la mtumiaji / neno siri macho ni sahihi."
#LOGIN_ERROR_STRING = "An error occurred while processing your login"
LOGIN_ERROR_STRING = "Kosa ilitokea wakati usindikaji kuingia yako"
#INVALID_LOGIN_STRING = "Invalid Login"
INVALID_LOGIN_STRING = "Mlango batili"
#DATA_RECORDING_FAILED_STRING = "Data recording failed"
DATA_RECORDING_FAILED_STRING = "Takwimu kurekodi kushindwa"
#LOGOUT_ERROR_STRING = "An error occurred while logging you out"
LOGOUT_ERROR_STRING = "Ni kosa ilitokea wakati magogo nje"
#NOT_FOUND_STRING = "Resource not found"
NOT_FOUND_STRING = "Nyenzo haikupatikana"
#ERROR_STRING = "An error occurred"
ERROR_STRING = "Ni kosa ilitokea"
#LOGGED_OUT_STRING = "You have been logged out."
LOGGED_OUT_STRING = "Umekuwa watumiaji nje."


class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer): pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    # Paths to the resources
    home_path = "/"
    css_path = "/style.css"
    css_file = "noradioactive.css"
    manual_path = "/manual"
    manual_file = "noradioactive.doc"
    icon_path = "/favicon.ico"
    icon_file = "noradioactive.ico"
    background_path = "/background.jpg"
    background_file = "noradioactive.jpg"
    login_path = "/login"
    logout_path = "/logout"
    register_path = "/register"
    reading_path = "/reading"
    dump_path = "/dump"
    # Parameters for accessing the database dump
    dump_allowed = False
    dump_auth_attr = "auth"
    dump_auth_value = "radioidar"

    # Secret used to generate sessions
    secret = "noradioactiveinjection"

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
        <p>[<a href='""" + home_path + """'>""" + HOME_STRING + """</a>][<a href='""" + register_path + """'>""" + \
        REGISTER_STRING + """</a>][<a href='""" + manual_path + """'>""" + DOCUMENTATION_STRING + \
        """</a>][<a href='""" + logout_path + """'>""" + LOGOUT_STRING + """</a>]</p>
      </div>
    </div>
  </body>
</html>
"""
    
    
    def sanitize(self, string):
        allowed = """ ~{}[$%^&|<>]\'"+=*#@.,:;!?()-/_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"""
        if string == None:
            return ""
        for c in string:
            if c not in allowed:
                return ""
        return string
	
    
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

	
    def style(self, params):
        self.send_response(200)	
        self.send_header('Content-type', 'text/css')
        self.end_headers()

        try:
            data = open(self.css_file, "r").read()
            self.wfile.write(data)
        except Exception, err:
            self.logger.error("Cannot access the CSS file: %s" % str(err))
            return 1
        return 0
        

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


    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % (TITLE_STRING, TITLE_STRING))

        # Checks if the user is logged in
        session = self.auth()
        self.logger.debug("Session: %s" % session)
        
        # The user is not logged in: prints the login and registration forms
        if session == None:
            self.wfile.write("""
<table>
<tr>
<td>
<p>""" + INTRO_STRING + """<p>
<hr />
<p>""" + LOGIN_STRING + """</p>

<fieldset>
  <legend>""" + LOGIN_FIELDSET_STRING + """</legend>
  <form name="login" action='""" + self.login_path + """' method="post">
    <p>""" + USERNAME_FIELD_STRING + """: <input type="text" name="username" /></p>
    <p>""" + PASSWORD_FIELD_STRING + """: <input type="password" name="password" /></p>
    <p><input type="submit" name="submit" value='""" + LOGIN_SUBMIT_STRING + """'></p>
  </form>
</fieldset>
</td>
<td>
<div id="image_container"><img id="image" src="background.jpg" /></div>
</td>
</tr>
</table>
""")
        # The user has a valid session: prints his/her data
        else:
            username = self.sessions.get(session).get('username')
            columns = self.data.get(username)
            
            self.wfile.write("""
<p>""" + WELCOME_STRING + """ """ + username + """ [""" + \
SERIAL_STRING + """: """ +  columns.get('serial') + """]</p>
<pre>
""")
            for column in columns.keys():
                if column == 'serial':
                    continue
                if column == 'password':
                    continue
                self.wfile.write("""
%s: %s
""" % (column, columns.get(column)))
            self.wfile.write("""
</pre>""")                 
            self.wfile.write("""
<p>""" + SUBMIT_READING_STRING + """: </p>
<fieldset>
  <legend>""" + FIELDSET_READING_STRING + """</legend>
  <form name="reading" action='""" + self.reading_path + """' method="post">
    <p>""" + LOCATION_FIELD_STRING + """: <input type="text" name="location" /></p>
    <p>""" + RADIO_FIELD_STRING + """: <input type="text" name="radioactivity" /></p>
    <p><input type="submit" name="submit" value='""" + READING_SUBMIT_STRING + """' /></p>
  </form>
</fieldset>
""")
        
        self.wfile.write(self.footer)
        return
    

    def register(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
       
        self.wfile.write(self.header % (REGISTER_STRING, REGISTER_STRING))
        self.wfile.write("""
<fieldset>
  <legend>""" + REGISTER_STRING + """</legend>
  <form name="register" action='""" + self.register_path + """' method="post">
    <p>""" + USERNAME_FIELD_STRING + """: <input type="text" name="username" /></p>
    <p>""" + PASSWORD_FIELD_STRING + """: <input type="password" name="password" /></p>
    <p>""" + SERIAL_FIELD_STRING + """: <input type="text" name="serial" /></p>
    <p><input type="submit" name="submit" value='""" + REGISTER_SUBMIT_STRING + """'></p>
  </form>
</fieldset>""")
        self.wfile.write(self.footer)
        return

    
    def manual(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Dumps the database
        self.wfile.write(self.header % (MANUAL_STRING, MANUAL_STRING))
        self.wfile.write("""<p>""" + MANUAL_DATA_STRING + """</p>""")
        
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
        self.wfile.write(self.header % (DATABASE_STRING, DATABASE_STRING))
        result = self.data.get_range()
        
        self.wfile.write("""<p>""" + DATA_STRING + """</p>""")
        
        self.wfile.write("""
<pre>
""")
        for key, columns in result:
            self.wfile.write("""
%s:
""" % key)
            for column in columns:
                self.wfile.write("""
  %s: %s
""" % (str(column), columns[column]))
            
        self.wfile.write("""
</pre>
""")
        self.wfile.write("""<p>""" + SESSIONS_STRING + """</p>""")
        result = self.sessions.get_range()
        self.wfile.write("""
<pre>
""")
        for key, columns in result:
            self.wfile.write("""
%s:
""" % key)
            for column in columns:
                self.wfile.write("""
  %s: %s
""" % (str(column), columns[column]))
            
        self.wfile.write("""
</pre>
""")
				
        self.wfile.write(self.footer)
        return


    def auth(self):
        cookies = self.headers.getheaders('Cookie')
        if cookies == None or len(cookies) == 0:
            return None
        self.logger.debug("Received cookies: %s"% str(cookies))
        session = None
        for cookie in cookies:
            try:
                attr_vals = cookie.split(';')
                for attr_val in attr_vals:
                    attr_val = attr_val.strip()
                    self.logger.debug("Considering attribute/value pair: %s" % str(attr_val))
                    attribute, value = attr_val.split('=')
                    if attribute == "session":
                        session = value
            except Exception, err:
                self.logger.debug("Error in parsing cookie %s: %s" % (str(cookie), str(err)))
                return False
        
        if session == None:
            return None
        try:
            columns = self.sessions.get(session)
            username = columns.get('username')
        except Exception, e:
            self.logger.error("Authentication failed for session: %s (%s)" % (session, str(e)))
            return None
        
        return session

        
    def reading(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % (RECORD_READING_STRING, RECORD_READING_STRING))
        
        session = self.auth()
        if session == None:
            self.wfile.write("""<p>""" + NOT_LOGGED_STRING + """</p>""")
            self.wfile.write(self.footer)
            return
        username = self.sessions.get(session).get('username')
        
        try:
            location = self.sanitize(form.getfirst("location"))
            radioactivity = self.sanitize(form.getfirst("radioactivity"))
            
            if location == "" or radioactivity == "":
                raise Exception("empty parameter(s)")
            
            self.logger.debug("Requested recording: location [%s] -> radioactivity [%s]" % (location, radioactivity))
            
            if location != "password" and location != "serial": 
                self.data.insert(username, {location: radioactivity})       
        
            self.wfile.write("""
<p>""" + READING_RECORDED_STRING + """</p>
""")
            result = self.data.get_range()
            colos = list()
            for key, columns in result:
                if key == username:
                    continue
                if columns.has_key(location):
                    colos.append(key)
            if len(colos) > 0:
                self.wfile.write("""
<p>""" + COLOCATED_WORKERS_STRING + """:</p>
<ul>
""")
                for u in colos:
                   self.wfile.write("""
<li>%s</li>
""" % u)
                self.wfile.write("""
</ul>
""")
            
            
            self.wfile.write(self.footer)
        except Exception, err:
            self.logger.error("An error occurred when recording your reading: %s" % str (err))
            self.wfile.write("""
<p>""" + DATA_RECORDING_FAILED_STRING + """: %s.</p>
""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            return
        return


    def process_register(self, form):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(self.header % (REGISTRATION_STRING, REGISTRATION_STRING))

        try:
            username = form.getfirst("username")
            password = form.getfirst("password")
            serial = form.getfirst("serial")

            if username == "" or password == "" or serial == "" or username == None or password == None or serial == None:
                raise Exception("empty parameter(s)")
            
            username = self.sanitize(username.strip())
            password = self.sanitize(password.strip())
            serial = self.sanitize(serial.strip())
            
            self.logger.debug("Requested registration with username [%s], password [%s], and serial [%s]" % 
                              (username, password, serial))
            if password != "":
                md5 = hashlib.md5()
                md5.update(password)
                password = md5.hexdigest()
            self.data.insert(username, {'password': password})
            
            if serial != "":
                self.data.insert(username, {'serial': serial})       
        
            self.wfile.write("""
<p>""" + USER_REGISTERED_STRING + """</p>
""")
            self.wfile.write(self.footer)
        except Exception, err:
            self.logger.error("An error occurred when registering your account: %s" % str (err))
            self.wfile.write("""
<p>""" + USER_REGISTRATION_FAILED_STRING + """: %s.</p>
""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            return
        return


    def login(self, form):
        try:
            username = self.sanitize(form.getfirst("username"))
            password = self.sanitize(form.getfirst("password"))

            self.logger.debug("Requested login with username [%s] and password [%s]" % (username, password))
            md5 = hashlib.md5()
            md5.update(password)
            password = md5.hexdigest()

            result = self.data.get(username)
            authenticated = True
            if not result.has_key('password'):
                authenticated = False
            if result['password'] != "" and result['password'] != password:
                authenticated = False
            
            if authenticated:
                # Computes the session token
                md5 = hashlib.md5()
                md5.update(str(time.time()) + username + password + self.secret)
                session = md5.hexdigest()

                self.sessions.insert(session, {'username': username})
    
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                self.wfile.write(self.header % (INVALID_LOGIN_STRING, INVALID_LOGIN_STRING))
                self.wfile.write("""
<p>""" + AUTHENTICATION_FAILED_STRING + """</p>
""")
                self.wfile.write(self.footer)
                self.logger.error("Invalid login with username [%s] and password [%s]" % (username, password))
                return

                        
        except Exception, err:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(self.header % (INVALID_LOGIN_STRING, INVALID_LOGIN_STRING))
            self.wfile.write(LOGIN_ERROR_STRING + """: %s""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            self.logger.error("An error occurred in processing the login: %s" % str(err))
            return
                         
        # Success: redirects the user to the home page and sets the cookie
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '%s' % self.home_path)
        self.send_header('Set-Cookie', "session=%s" % session)
        self.end_headers()
        return

    
    def logout(self, params):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(self.header % ("Logout", "Logout"))

            session = self.auth()

            # If there is no session, redirect to home page
            if session == None:
                self.wfile.write("""<p>""" + NOT_LOGGED_STRING + """</p>""")
                self.wfile.write(self.footer)
                return

            self.sessions.remove(session)
        except Exception, err:
            self.wfile.write(LOGOUT_ERROR_STRING + """: %s""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            self.logger.error("An error occurred in processing the logout: %s" % str(err))
            return
                         
        self.wfile.write("""
<p>""" + LOGGED_OUT_STRING + """</p>
""")
        self.wfile.write(self.footer)
        return


    def do_GET(self):
        try:
            self.logger.debug("Received GET request with path: %s" %  self.path)

            # Parses the request
            req = urlparse.urlparse(self.path)
            self.logger.debug("Received request resource: %s" % req.path)
            
            params = urlparse.parse_qs(req.query)
            self.logger.debug("Received parameters: %s" % str(params))
            
            # Retrieves the data and session connections
            self.data = pycassa.columnfamily.ColumnFamily(RequestHandler.pool, RequestHandler.data_family)
            self.sessions = pycassa.columnfamily.ColumnFamily(RequestHandler.pool, RequestHandler.session_family)   
            
            # Dispatches the request to the appropriate method
            if req.path == self.home_path:
                self.home(params)
                return

            elif req.path == self.register_path:
                self.register(params)
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
            
            else:
                self.send_error(404, NOT_FOUND_STRING + ': %s' % self.sanitize(self.path))                
                return
            # Never reached
            return
        except Exception, err:
            self.wfile.write(ERROR_STRING + ": " + self.sanitize(str(err)))
            self.logger.error("An error occurred: " + str(err))
            et, ev, tb = sys.exc_info()
            traceback.print_tb(tb)
            return


    def do_POST(self):
        try:
            self.logger.debug("Received POST request with path: %s" %  self.path)

            # Parses the request
            req = urlparse.urlparse(self.path)
            self.logger.debug("Received request resource: %s" % req.path)
            
            # Extracts the post data
            form = cgi.FieldStorage(fp=self.rfile, 
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD':'POST',
                                             'CONTENT_TYPE':self.headers['Content-Type'],
                                             })

            self.logger.debug("Received parameters: %s" % str(form))
            
            # Retrieves the data and session connections
            self.data = pycassa.columnfamily.ColumnFamily(RequestHandler.pool, RequestHandler.data_family)
            self.sessions = pycassa.columnfamily.ColumnFamily(RequestHandler.pool, RequestHandler.session_family)   
            
            # Dispatches the request to the appropriate method
            if req.path == self.login_path:
                self.login(form)
                return

            elif req.path == self.register_path:
                self.process_register(form)
                return
            
            elif req.path == self.reading_path:
                self.reading(form)
                return

            else:
                self.send_error(400, NOT_FOUND_STRING + ': %s' % self.sanitize(self.path)) 
                return

            # Never reached
            return
        except Exception, err:
            self.wfile.write(ERROR_STRING + ": " + self.sanitize(str(err)))
            self.logger.error("An error occurred: " + str(err))
            # Uncomment the following two lines to obtain more complete error information
            #et, ev, tb = sys.exc_info()
            #traceback.print_tb(tb)
            return


def usage(fname):
    print "%s [-d (debug)] [-p <port>] [-b <server>] [-k <keyspace>] [-l <log file>] [-i <init file>]" % fname


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv

    debug = False
    port = 9292
    keyspace = "myspace"
    data_family = "data"
    session_family = "sessions"
    log_level = logging.INFO
    log_file = None
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    initialize = False
    init_file = None
    db_hostname = 'localhost'
    db_port = 9160 
    
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "dhp:k:l:i:")
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
                db_hostname, db_port = split(a, ":")
            if o == "-k":
                keyspace = a
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
    logger = logging.getLogger('noradioactive')
    RequestHandler.logger = logger
    logger.debug("Initialization...")
    
    # Makes sure that the keyspace and column families exist
    try:
        logger.debug("Connecting to database %s:%s" % (str(db_hostname), str(db_port)))
        sysmgr = pycassa.system_manager.SystemManager("%s:%s" % (str(db_hostname), str(db_port)))
        logger.debug("Connection successful")
        
        keyspaces = sysmgr.list_keyspaces()
        logger.debug("Keyspaces: %s" % str(keyspaces))
        if initialize and keyspace in keyspaces:
            logger.debug("Dropping keyspace: %s" % keyspace)
            sysmgr.drop_keyspace(keyspace)
        
        keyspaces = sysmgr.list_keyspaces()
        if not keyspace in keyspaces:
            logger.debug("Creating keyspace: %s" % keyspace)
            sysmgr.create_keyspace(keyspace, pycassa.system_manager.SIMPLE_STRATEGY, {'replication_factor': '1'})
        families = sysmgr.get_keyspace_column_families(keyspace).keys()
        logger.debug("Families: %s" % str(families))
        if not data_family in families:
            logger.debug("Creating column family: %s" % data_family)
            sysmgr.create_column_family(keyspace, data_family, column_validation_classes=None)
        if not session_family in families:
            logger.debug("Creating column family: %s" % session_family)
            sysmgr.create_column_family(keyspace, session_family, column_validation_classes=None)
    except Exception, err:
            logger.error("Failed to initialize the database: %s" % str(err))
            et, ev, tb = sys.exc_info()
            traceback.print_tb(tb)
            return 1        
    
    # Makes sure that the database exists
    try:
        RequestHandler.pool = pycassa.pool.ConnectionPool(keyspace, ['%s:%s' % (str(db_hostname), str(db_port))]) 
        data = pycassa.columnfamily.ColumnFamily(RequestHandler.pool, data_family)
        session = pycassa.columnfamily.ColumnFamily(RequestHandler.pool, session_family)        
    except Exception, e:
        logger.error("Missing or corrupted database %s: %s" % (keyspace, str(e)))
        return 1

    
    # If the database needs to be initialized, reads the values from the init file
    if initialize:
        try:
            config = ConfigParser.ConfigParser()
            config.read(init_file)
            for username in config.sections():
                password = config.get(username, "password")
                serial = config.get(username, "serial")
                md5 = hashlib.md5()
                md5.update(password)
                password = md5.hexdigest()
                data.insert(username, {'password': password, 'serial': serial})        
        except Exception, err:
            logger.error("Failed to initialize the database: %s" % str(err))
            et, ev, tb = sys.exc_info()
            traceback.print_tb(tb)
    
    RequestHandler.data_family = data_family
    RequestHandler.session_family = session_family
    
    if debug:
        result = data.get_range()
        for key, columns in result:
            logger.debug("%s => %s" % (key, str(columns)))
        result = session.get_range()
        for key, columns in result:
            logger.debug("%s => %s" % (key, str(columns)))
         
    # Starts the web server
    logger.debug("Listening on port %d" % port)
    try:
        logger.info("Starting noradioactive service...")    
        httpd = ThreadingHTTPServer(('', port), RequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down noradioactive...')
        httpd.socket.close()
    except Exception, e:
       logger.error("Error starting noradioactive: %s" % str(e))
       return 1

if __name__ == '__main__':
    sys.exit(main())
