#!/usr/bin/python

import os
import sys
import cgi
import cgitb; cgitb.enable()
import string
from types import StringType
import re

flaglen = 40
validatebin="/ctf/validate"

teams = [
        "10.10.10.0/24",
        "10.10.20.0/24",
        "10.10.30.0/24",
        "10.20.10.0/24",
        "10.30.10.0/24",
        "10.40.10.0/24",
        "10.40.20.0/24",
        "10.50.10.0/24",
        "10.60.10.0/24",
#        "10.70.10.0/24",
        "10.90.10.0/24",
        "10.100.10.0/24",
        "10.110.10.0/24",
        "10.120.10.0/24",
        "10.130.10.0/24",
        "10.140.10.0/24",
        "10.150.10.0/24",
        "10.160.10.0/24",
        "10.160.20.0/24"
        ]
	

def printform():
   print """
   <center><h1>Flag Submission</h1></center>
   <form action="submitflag.py" method="get" >
   <p>Enter your flag here:
   <input type="text" name="flag" maxlength=\"""" + str(flaglen) + """\" size=\"""" + str(flaglen) + """\"/>
   <button type="submit">Submit Flag</button>
   </form>
   """

def printerror(msg):
   print """
   <center><h1>Error submitting flag</h1></center><br>
   <p>"""  + msg  + "</p>"
   print """
   <hr>
   <form action="submitflag.py" method="get" >
   <p>Try again, enter your flag here:
   <input type="text" name="flag" maxlength=\"""" + str(flaglen) + """\" size=\"""" + str(flaglen) + """\"/>
   <button type="submit">Submit Flag</button>
   </form>
   """

def printsuccess():
   print """
   <center><h1>Flag Accepted</h1></center><br>
   <p>The score will be updated in just a moment
   <hr>
   <form action="submitflag.py" method="get" >
   <p>Submit another flag:
   <input type="text" name="flag" maxlength=\"""" + str(flaglen) + """\" size=\"""" + str(flaglen) + """\"/>
   <button type="submit">Submit Flag</button>
   </form>
   """

def cidrmatch(cidr, ip):
   res = re.match("([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)/([0-9]*)", cidr)
   if not res or res.lastindex != 5:
      return 0
    	
   a = int(res.group(1))
   b = int(res.group(2))
   c = int(res.group(3))
   d = int(res.group(4))
   mask = int(res.group(5))
   if a > 255 or b > 255 or c > 255 or d > 255 or mask > 32:
      return 0
   if a < 0 or b < 0 or c < 0 or d < 0 or mask < 0:
      return 0

   net2 = (a * 16777216) + (b * 65536) + (c * 256) + d
   mask2 = pow(2, (32 - mask)) - 1
   mask2 = ~mask2 

   res = re.match("([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)", ip)
   if not res or res.lastindex != 4:
      return 0
   
   a = int(res.group(1))
   b = int(res.group(2))
   c = int(res.group(3))
   d = int(res.group(4))
   
   if a > 255 or b > 255 or c > 255 or d > 255:
      return 0
   if a < 0 or b < 0 or c < 0 or d < 0:
      return 0
  
   ip2 = (a * 16777216) + (b * 65536) + (c * 256) + d
 
   return (net2 & mask2) == (ip2 & mask2)


def lookupteam():
   if not os.environ.has_key('REMOTE_ADDR'):
      printerror("I cannot figure what team you belong to")
      return -1

   host  = os.environ['REMOTE_ADDR']
   
   for i in range(len(teams)):
      if cidrmatch(teams[i], host):
	return i + 1

   printerror("You don't seem to belong to any team I know about. If this is incorrect, contact the CTF admin team")
   return -1

def decode(str):
   t = string.maketrans(".", "/")
   return str.translate(t)

def checkflag(flag):
   if not isinstance(flag, StringType):
      printerror("No hacking please!")
      return
   if len(flag) > flaglen:
      printerror("The textbox has a max size for a reason, no hacking please!");
      return
   if len(flag) < flaglen:
      printerror("A flag is " + str(flaglen) + " characters long. You submitted a too short flag.");
      return
   if re.search("[^a-zA-Z0-9=\+/\.]", flag):
      printerror("The flag contains illegal characters. It cannot be a valid flag.")
      return

   teamno = lookupteam()
   if teamno == -1:
      return

   flag = decode(flag)

   ret = os.spawnl(os.P_WAIT, validatebin, validatebin, str(teamno), flag)
  
   if ret == 0:
	printsuccess()
   elif ret == 1:
	printerror("Internal error in the scorebot! Please try again later.")
   elif ret == 2:
	printerror("The flag you submitted is not a valid flag.")
   elif ret == 3:
	printerror("The flag you submitted is too old.")
   elif ret == 4:
	printerror("You have submitted this flag before. Try to find a new flag instead.")
   elif ret == 5:
	printerror("The flag you submitted belogs to your own team. Are you trying to hack yourself?")
   elif ret == 6:
        printerror("The service you submitted a flag for is maxed out." +
	           "You will not be awarded any more points for hacking this service." +
                   "Try to hack another service.")
   else:
	printerror("Very bad error, contact the CTF admin team.")

##### MAIN ######
print """Content-Type: text/html

<html><head><title>CTF Flag Submission</title></head>
<body>
"""

form = cgi.FieldStorage()

if not form.has_key("flag"):
	printform()
else:
   value = form.getvalue("flag", "")
   if isinstance(value, list):
      printerror("You cannot submit more than one flag at a time")
   else:
      checkflag(value)

print "</body></html>"
