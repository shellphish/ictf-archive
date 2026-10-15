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
mainpg = pybrowse.Browser("http://" + target + "/~register/register.html", personality, debug=1)
mainpg = mainpg.doRedirects()
mainpg.open()
mainpg.parse()
#print mainpg.page

# Get the form, and search for flag (if cookie is provided)
if username != "":
   try:
	f = mainpg.forms[1]

	f.fields["wwid"]     = username
	f.fields["password"] = password
	resultingPage = f.click(None)
	resultingPage = resultingPage.doRedirects()
	
	data = resultingPage.page
        #print data	
	start = data.find("td>First:</td><td><input")
	if start < 0:
		print "Flag not found"
	else:
		oldflag = username
		#print "OLD = %s"%oldflag
   except Exception, e:
      print "Exception getting flag %s" % (e)

# Now create a new flag
newuser     = getRandomString(8)
newpassword = getRandomString(8)
newcookie   = newflag + ":" + newpassword
 
# The flag is set in the same form (image search)
try:
   f = mainpg.forms[0]
   f.fields["first"]      = newuser
   f.fields["last"]       = newuser
   f.fields["dob"]        = "18-12-63" 
   f.fields["wwid"]       = newflag
   f.fields["email"]      = "%s@%s.com"%(newuser,newuser)
   f.fields["password"]   = newpassword
   resultingPage = f.click(None)
   resultingPage = resultingPage.doRedirects()
   if resultingPage.status != 200:
      print "Error setting new flag"
except Exception, e:
   print "Exception setting flag %s" % (e)
   
print "FLAG:" + oldflag
print "COOKIE:" + newcookie


