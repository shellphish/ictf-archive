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
import time

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
    login_path = "/login"
    logout_path = "/logout"
    find_path = "/find"
    register_path = "/register"
    dump_path = "/dump"
    profile_path = "/profile"
    update_path = "/update"
    picture_path = "/picture"

    # Parameters for accessing the database dump
    dump_auth_attr = "auth"
    dump_auth_value = "s3cr3t"

    # Secret used to generate sessions
    secret = "youwillneverguessthissecretphrase"

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
        <p>[<a href='""" + home_path + """'>Home</a>][<a href='find'>Find Friends</a>][<a href='""" + logout_path + """'>Logout</a>]</p>
      </div>
    </div>
  </body>
</html>
"""

    # Sanitizes input from the user
    def sanitize(self, string):
        allowed = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        #allowed = "'.,:;!?()-/_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
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
  background: #2B60DE;
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

    def picture(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'image/JPEG')
        self.end_headers()
        gender = int(params["display"][0])

        try:
            f = open(gender and "/home/seclab/he.png" or "/home/seclab/she.png", "r")
            self.wfile.write(f.read())
        except Exception, err:
            self.logger.debug("Cannot open image: %s" % str(err))

    def profile(self,params):
      
	username = self.sanitize(params["username"][0])
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
	cur = self.conn.cursor()
	cur.execute("""select username,day,month,year,gender from users where username=?;""", (username, ))
	result = cur.fetchone()
	if result == None:
	    self.wfile.write("There was an error retrieving your data.")
	else:
	    username = result[0]
	    day = result[1]
	    month = result[2]
	    year = result[3]
	    gender = result[4]
	    image = gender and "he.png" or "she.png"
	    self.wfile.write("""

<table bgcolor="#2B60DE" width="1024">
<tr>
<td><h2><span style="color:white">lityaBook</span></h2></td>
<td>
<td>
</td>
</tr>
</table>
<table>
<tr>
<td width=800><p>%s</p><br><br><p> Born on %s/%s/%s</p></td>
<td><img src='/picture?display=%s' border=1></td>
</tr>
</table>
<table>
""" % (username,month,day,year,gender))
	cur = self.conn.cursor()
	cur.execute("""select content,date from posts where username=?;""",(username,))
	for post in cur.fetchall():
	  self.wfile.write("""
<tr>
<td>%s<br><br></td>
</tr>
<tr>
<td>Posted on %s<br><br></td>
</tr>
		      """%(post[0],time.ctime(post[1])))
	self.wfile.write("""</table>""")

	self.wfile.write(self.footer)
	return

    # Prints the home page
    def home(self, params):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

	#self.wfile.write(self.header % ("Home", "Home Page"))
        authenticated = False

	if "session" in params:
	  session = params["session"][0] 
	  cur = self.conn.cursor()
	  cur.execute("select * from users where session=?;",(session,))
	  if cur.fetchall() != []:
	    authenticated = True
	else:
	  session = self.auth()
	  authenticated = True
	if not authenticated or session == None:
            self.wfile.write("""
<html>
<title>lityabook</title>
<table bgcolor="#2B60DE" width="1024">
<tr>
<td><h2><span style="color:white">lityaBook</span></h2></td>
<td>
  <form action="%s" method="post">
    <span style="color:white">Username:</span> <input type="text" name="username" />
    <span style="color:white">Password:</span> <input type="password" name="password" />
    <span style="color:white"></span> <input type="hidden" name="session" value="%s"/>
    <input type="submit" name="submit" value="login">
  </form>
</tf>
</tr>
</table>
<table width="1024">
<tr>
<td>
<fieldset>
  <legend>Not registered? Sign up!</legend>
  <form action="%s" method="post">
    <p>Username: <input type="text" name="username" /></p>
    <p>Password: <input type="password" name="password" /></p>
    <select name="gender">
    <option> gender </option>
    <option value ="1">Male</option>
    <option value ="0">Female</option>
    </select><br><br>
    <select name="day">
      <option> day </option>
      <option value="1">1</option>
      <option value="2">2</option>
      <option value="3">3</option>
      <option value="4">4</option>
      <option value="5">5</option>
      <option value="6">6</option>
      <option value="7">7</option>
      <option value="8">8</option>
      <option value="9">9</option>
      <option value="10">10</option>
      <option value="11">11</option>
      <option value="12">12</option>
      <option value="13">13</option>
      <option value="14">14</option>
      <option value="15">15</option>
      <option value="16">16</option>
      <option value="17">17</option>
      <option value="18">18</option>
      <option value="19">19</option>
      <option value="20">20</option>
      <option value="21">21</option>
      <option value="22">22</option>
      <option value="23">23</option>
      <option value="24">24</option>
      <option value="25">25</option>
      <option value="26">26</option>
      <option value="27">27</option>
      <option value="28">28</option>
      <option value="29">29</option>
      <option value="30">30</option>
      <option value="31">31</option>
    </select>
    <select name="month">
    	<option> month </option>
	<option value="January">January</option>
	<option value="Febuary">Febuary</option>
	<option value="March">March</option>
	<option value="April">April</option>
	<option value="May">May</option>
	<option value="June">June</option>
	<option value="July">July</option>
	<option value="August">August</option>
	<option value="September">September</option>
	<option value="October">October</option>
	<option value="November">November</option>
	<option value="December">December</option>
    </select>
    <select name="year">
      <option> year </option>
      <option value="1950">1950</option>
      <option value="1951">1951</option>
      <option value="1952">1952</option>
      <option value="1953">1953</option>
      <option value="1954">1954</option>
      <option value="1955">1955</option>
      <option value="1956">1956</option>
      <option value="1957">1957</option>
      <option value="1958">1958</option>
      <option value="1959">1959</option>
      <option value="1960">1960</option>
      <option value="1961">1961</option>
      <option value="1962">1962</option>
      <option value="1963">1963</option>
      <option value="1964">1964</option>
      <option value="1965">1965</option>
      <option value="1966">1966</option>
      <option value="1967">1967</option>
      <option value="1968">1968</option>
      <option value="1969">1969</option>
      <option value="1970">1970</option>
      <option value="1971">1971</option>
      <option value="1972">1972</option>
      <option value="1973">1973</option>
      <option value="1974">1974</option>
      <option value="1975">1975</option>
      <option value="1976">1976</option>
      <option value="1977">1977</option>
      <option value="1978">1978</option>
      <option value="1979">1979</option>
      <option value="1980">1980</option>
      <option value="1981">1981</option>
      <option value="1982">1982</option>
      <option value="1983">1983</option>
      <option value="1984">1984</option>
      <option value="1985">1985</option>
      <option value="1986">1986</option>
      <option value="1987">1987</option>
      <option value="1988">1988</option>
      <option value="1989">1989</option>
      <option value="1990">1990</option>
      <option value="1991">1991</option>
      <option value="1992">1992</option>
      <option value="1993">1993</option>
      <option value="1994">1994</option>
      <option value="1995">1995</option>
      <option value="1996">1996</option>
      <option value="1997">1997</option>
      <option value="1998">1998</option>
      <option value="1999">1999</option>
      <option value="2000">2000</option>
      <option value="2001">2001</option>
      <option value="2002">2002</option>
      <option value="2003">2003</option>
      <option value="2004">2004</option>
      <option value="2005">2005</option>
      <option value="2006">2006</option>
      <option value="2007">2007</option>
      <option value="2008">2008</option>
      <option value="2009">2009</option>
    </select>
    <p><input type="submit" name="submit" value="Register"></p>
  </form>
</fieldset>
</td>
</tr>
</table>
""" % (self.login_path, session,self.register_path))
            #return
        # The user has a valid session: prints his/her data
        else:
            cur = self.conn.cursor()
            cur.execute("""select username,password,data,session,gender from users where session=?""", (session, ))
            result = cur.fetchone()
            if result == None:
                self.wfile.write("There was an error retrieving your data.")
            else:
                username = result[0]
                password = result[1]
                data = result[2]
                session = result[3]
		gender = result[4]
		image = gender and "he.png" or "she.png"
                self.wfile.write("""

<table bgcolor="#2B60DE" width="1024">
<tr>
<td><h2><span style="color:white">lityaBook</span></h2></td>
<td>
<td>
</td>
</tr>
</table>
<table>
<tr>
<td width=800><p>Welcome %s</p></td>
<td><img src='/picture?display=%s' border=1></td>
</tr>
</table>
<hr>
<p>What are you doing?</p><br>
<form action="update" method="post">
<textarea name="update" COLS=40 ROWS=6></textarea>
<input type="submit" name="submit" value="Tell everybody!">
</form>
<table>
""" % (username,gender))
		cur = self.conn.cursor()
		cur.execute("""select content,date from posts where username=?;""",(username,))
		for post in cur.fetchall():
		  self.wfile.write("""
<tr>
<td>%s<br><br></td>
</tr>
<tr>
<td>Posted on %s<br><br></td>
</tr>
		      """%(post[0],time.ctime(post[1])))
		self.wfile.write("""</table>""")

        cur = self.conn.cursor()
        cur.execute("""select session from users where username="edeo";""")
	s = cur.fetchone()[0]
	if s == session:
	  with open("/home/seclab/flag") as f:
	    for line in f.readlines():
	      flag = line.split()[0]
	  self.wfile.write("%s\n"%flag)
	self.wfile.write(self.footer)
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
        self.wfile.write(self.header % ("Database", "The Database"))
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
        self.wfile.write(self.footer)
        return


    def auth(self):
        cookie = self.headers.getheaders('Cookie')
        if cookie == None or len(cookie) == 0:
            return None
        try:
            self.logger.debug("Received cookie: %s"% str(cookie))
            session = cookie[0].split('=')[1].split(";")[0]
        except Exception, err:
            self.logger.debug("Error in parsing cookie %s: %s" % (cookie[0], str(err)))
            return None
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
	self.wfile.write("""
<table bgcolor="#2B60DE" width="1024">
<tr>
<td><h2><span style="color:white">lityaBook</span></h2></td>
</tr>
</table>""")
	#self.wfile.write(self.header % ("Registration", "Registration"))

        try:
            username = self.sanitize(form.getfirst("username"))
            password = self.sanitize(form.getfirst("password"))
	    gender = self.sanitize(form.getfirst("gender"))
            day = self.sanitize(form.getfirst("day"))
            month = self.sanitize(form.getfirst("month"))
            year = self.sanitize(form.getfirst("year"))
            data = self.sanitize(form.getfirst("data"))

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
                cur.execute("""insert into users values (?,?,?,?,?,?,?,?);""", (username, 
                                                                              password, 
									      gender,
									      day,
									      month,
									      year,
                                                                              data, 
                                                                              session))
                self.conn.commit()
                cur.close()
                self.wfile.write("""
<p>User successfully registered.</p>
""")
                self.wfile.write(self.footer)
        except Exception, err:
            self.logger.error("An error occurred when registering your account: %s" % str (err))
            return
        return


    # Login 
    def login(self, form):
        try:
            username = self.sanitize(form.getfirst("username"))
	    password = self.sanitize(form.getfirst("password"))
            session = self.sanitize(form.getfirst("session"))
            
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
	        self.wfile.write("""	
<table bgcolor="#2B60DE" width="1024">
<tr>
<td><h2><span style="color:white">lityaBook</span></h2></td>
</tr>
</table>""")
		#self.wfile.write(self.header % ("Login", "Invalid Login"))
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
	    if session == "None":
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
        self.send_header('Set-Cookie', "session=%s" % (session))
        self.send_header('Set-Cookie', "password=%s" % (password))
        self.end_headers()
        return


    # Logout
    def logout(self, params):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

	    self.wfile.write("""	
<table bgcolor="#2B60DE" width="1024">
<tr>
<td><h2><span style="color:white">lityaBook</span></h2></td>
</tr>
</table>""")
	    #self.wfile.write(self.header % ("Logout", "Logout"))

            session = self.auth()

            # If there is no session, redirect to home page
            if session == None:
                self.wfile.write("<p>Your are not logged in.</p>")
                self.wfile.write(self.footer)
                return

            cur = self.conn.cursor()
            cur.execute("""select username,password,session from users where session=?""", (session, ))
            result = cur.fetchone()
            if result == None:
                self.wfile.write("""
<p>There was an error retrieving your session.</p>
""")
                self.wfile.write(self.footer)
                return

            username = result[0]
            password = result[1]
            session = result[2]

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

    def find(self, params):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

	    #self.wfile.write(self.header % ("Find Friends", "find Friends"))
	    self.wfile.write("""
	     
<table bgcolor="#2b60de" width="1024">
<tr>
<td><h2><span style="color:white">lityabook</span></h2></td>
<td>
<td>
</td>
</tr>
</table>
<table>
	     """)
            session = self.auth()
	    cur = self.conn.cursor()
	    cur.execute("""select username,gender,day,month,year from users;""")
	    for person in cur.fetchall():
                self.wfile.write("""
<tr>
<td><b>Name:</b>   <a href="profile?username=%s">%s</a>   </td><td><b>Gender:</b>    %s   </td><td><b>Birth Date:</b>    %s</td><td>%s</td><td>%s</td>
</tr>
		"""%(person[0],person[0],person[1] and "Male" or "Female",person[2],person[3],person[4]))

	    self.wfile.write("""</table>""")
            # If there is no session, redirect to home page
            if session == None:
                self.wfile.write("<p>Your are not logged in.</p>")
                self.wfile.write(self.footer)
                return

	    self.wfile.write(self.footer)
	except Exception, err:
            self.wfile.write("""ERROR: An error occurred while logging you out: %s""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            cur.close()
            self.logger.error("An error occurred in processing the logout: %s" % str(err))
            return
                         
        return

    def update(self, form):
        try:
	    update = form.getfirst("update")
	    #self.send_response(200)
	    #self.send_header('Content-type', 'text/html')
	    #self.end_headers()

	    #self.wfile.write(self.header % ("Find Friends", "find Friends"))
	    #self.wfile.write("""
	     
#<table bgcolor="#2b60de" width="1024">
#<tr>
#<td><h2><span style="color:white">lityabook</span></h2></td>
#<td>
#<td>
#</td>
#</tr>
#</table>
#	     """)
            session = self.auth()

            # If there is no session, redirect to home page
            if session == None:
                self.wfile.write("<p>Your are not logged in.</p>")
                self.wfile.write(self.footer)
                return

	    self.conn = sqlite3.connect(RequestHandler.db)
	    cur = self.conn.cursor()
	    cur.execute("""select username from users where session=?;""",(session,))
	    result = cur.fetchone()
            
	    cur.execute("""insert into posts (username,content,date) values (?,?,?);""",(result[0],update,int(time.time())))
            self.conn.commit()

	    
	    
	    #self.wfile.write("%s %s"%(str(result[0]),update))
	    #self.wfile.write(self.footer)
	    cur.close()
	    self.home({})
	except Exception, err:
            self.wfile.write("""ERROR: An error occurred while logging you out: %s""" % self.sanitize(str(err)))
            self.wfile.write(self.footer)
            cur.close()
            self.logger.error("An error occurred in processing the logout: %s" % str(err))
            return
                         
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

            elif req.path == self.logout_path:
                self.logout(params)
                return

            elif req.path == self.find_path:
                self.find(params)
                return
            
	    elif req.path == self.profile_path:
                self.profile(params)
                return
	    
	    elif req.path == self.picture_path:
                self.picture(params)
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
            
	    elif self.path == self.update_path:
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
            cur.execute("""create table users (username text, password text, gender shortint, day shortint, month shortint, year shortint, data text, session text);""")
            config = ConfigParser.ConfigParser()
            config.read(init_file)

            for username in config.sections():
                try:
                    password = config.get(username, "password")
		    gender = config.get(username,"gender")
                    day = config.get(username, "day")
                    month = config.get(username, "month")
                    year = config.get(username, "year")
                    md5 = hashlib.md5()
                    md5.update(password)
                    password = md5.hexdigest()
                    data = config.get(username, "data")
                    session = "-"
                    cur.execute("""insert into users values (?,?,?,?,?,?,?,?);""", (username, 
                                                                                  password, 
										  gender,
										  day,
										  month,
										  year,
                                                                                  data, 
                                                                                  session))
                except Exception, e:
                    logger.error("Error while parsing init file: %s" % str(e))
                    raise
            conn.commit()
            cur.close()

            conn = sqlite3.connect(RequestHandler.db)
	    cur = conn.cursor()
	    cur.execute("""create table posts (username text,content text, date int);""")
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

if __name__ == '__main__':
    sys.exit(main())
