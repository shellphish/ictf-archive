#!/usr/bin/python

# To test, type something like: ./example_service.py www.google.com newflag user:pass

import pybrowse
import browserpersonality
import os, random, time, sys, string, re


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def getRandomString(len):
	ret = ""
	for i in range(len):
		ret += random.choice(alphabet)
	return ret


#### Main
target   = sys.argv[1]
newflag  = sys.argv[2]
if len(sys.argv) > 3 and sys.argv[3] != "":
	cookie = sys.argv[3]
	(username,password) = cookie.split(":")
else:
	cookie = ""
	username = ""
	password = ""

oldflag = ""



personality = browserpersonality.getRandomPersonality()

# Open the main webpage
mainpg = pybrowse.Browser("http://" + target + "/~pollit/pollit.html", personality, debug=0)
mainpg = mainpg.doRedirects()
mainpg.open()
mainpg.parse()
#print mainpg.page

# Get the form, and search for flag (if cookie is provided)
if username != "":
   try:
	f = mainpg.forms[1]

	f.fields["username"]   = username
	f.fields["pollid"]     = password
	f.fields["scope"]      = "local"
	f.fields["op"]         = "review"
	resultingPage = f.click(None)
	resultingPage = resultingPage.doRedirects()
	
	data = resultingPage.page	
	start = data.find("<tr><td>20</td><td>10</td>")
	if start < 0:
		print "Flag not found"
	else:
		oldflag = password
		#print "OLD = %s"%oldflag
   except Exception, e:
      print "Exception getting flag %s" % (e)

# Now create a new flag
newuser = getRandomString(8)
newcookie = newuser + ":" + newflag
 
# The flag is set in the same form (image search)
try:
   f = mainpg.forms[0]
   f.fields["username"]   = newuser
   f.fields["pollid"]     = newflag
   f.fields["schmidt"]    = "20" 
   f.fields["blitzkrieg"] = "10"
   f.fields["stallone"]   = "10"
   f.fields["blix"]       = "10"
   f.fields["schtrappe"]  = "10"
   f.fields["scope"]      = "local"
   f.fields["op"]         = "upload"
   resultingPage = f.click(None)
   resultingPage = resultingPage.doRedirects()
   if resultingPage.status != 200:
      print "Error setting new flag"
except Exception, e:
   print "Exception setting flag %s" % (e) 
   
print "FLAG:" + oldflag
print "COOKIE:" + newcookie


