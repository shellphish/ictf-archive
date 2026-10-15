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
mainpg = pybrowse.Browser("http://" + target + "/diebald/", personality, debug=0)
mainpg = mainpg.doRedirects()
mainpg.open()
mainpg.parse()
#print mainpg.page

links = ["/~diebald/cgi-bin/admin"]
if not mainpg.containsLinks(links):
   print "Mainpage does not contain all the links it is supposed to do"
   sys.exit(1)

  # Click on one random page
page = mainpg.click(links[0])
page = page.doRedirects()
page.parse()
if page.status != 200:
   print "Error loading subpage errorcode: " + str(page.status)
   sys.exit(1)

# Get the form, and search for flag (if cookie is provided)
if username != "":
   try:
	f = page.forms[2]
	
	f.fields["username"] = username
	f.fields["password"] = password
	f.fields["op"] = "gettask"
	
	resultingPage = f.click(None)
	resultingPage = resultingPage.doRedirects()
	
	data = resultingPage.page	
	start = data.find("<pre>")
	if start < 0:
		print "Flag not found"
	else:
		end = data.find("<",start+2)
		oldflag = data[start+6:end-1]
		#print "OLD = %s"%oldflag
   except Exception, e:
      print "Exception getting flag: %s" % (e)

# Now create a new flag
try:
   newuser = getRandomString(8)
   newpass = getRandomString(8)
   newcookie = newuser + ":" + newpass
 
   # The flag is set in the same form (image search)
   f = page.forms[0]
   f.fields["username"] = newuser
   f.fields["password"] = newpass
   f.fields["op"] = "create"
   resultingPage = f.click(None)
   resultingPage = resultingPage.doRedirects()
   if resultingPage.status != 200:
      print "Error setting new flag"

   f = page.forms[1]
   f.fields["username"] = newuser
   f.fields["password"] = newpass
   f.fields["task"] = newflag
   f.fields["op"] = "addtask"
   resultingPage = f.click(None)
   resultingPage = resultingPage.doRedirects()
   if resultingPage.status != 200:
      print "Error setting new flag"
except Exception, e:
   print "Exception setting flag %s" % (e)

print "FLAG:" + oldflag
print "COOKIE:" + newcookie
