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
	(username, secret) = cookie.split(":")
else:
	cookie   = ""
	username = ""
	secret   = ""
	
oldflag = ""



personality = browserpersonality.getRandomPersonality()

# Open the main webpage
mainpg = pybrowse.Browser("http://" + target + "/~feedback/cgi-bin/candidates.php", personality, debug=0)
mainpg = mainpg.doRedirects()
mainpg.open()
mainpg.parse()
#print mainpg.page
form = random.randint(0,4)

# Get the form, and search for flag (if cookie is provided)
if username != "":
   try:
	f = mainpg.forms[form]

	f.fields["name"]     = username
	f.fields["comment"]  = username
	f.fields["candidate"] = str(form)
	resultingPage = f.click(None)
	resultingPage = resultingPage.doRedirects()
	
	data = resultingPage.page
	if secret in data:
		oldflag = secret
		#print "OLD = %s"%oldflag
	else:
		print "Flag not found"
   except Exception, e:
      print "Exception getting flag %s" % (e)


# Now create a new flag
newuser     = getRandomString(8)
newcookie   = newuser+":"+newflag

# The flag is set in the same form (image search)
try:
   f = mainpg.forms[form]
   f.fields["name"]      = newuser
   f.fields["comment"]   = newflag
   f.fields["candidate"] = str(form)
   resultingPage = f.click(None)
   resultingPage = resultingPage.doRedirects()
   if resultingPage.status != 200:
      print "Error setting new flag"
except Exception, e:
   print "Exception setting flag %s" % (e) 

print "FLAG:" + oldflag
print "COOKIE:" + newcookie


