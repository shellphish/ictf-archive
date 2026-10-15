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
	# Cookie has <username>:<password> format
	(oldflag,amount) = cookie.split(":")
else:
	amount  = ""
	oldflag = ""


# Get a random browser personality (IE, Mozialla, Safari etc.)
personality = browserpersonality.getRandomPersonality()

# Open the main webpage
mainpg = pybrowse.Browser("http://" + target + "/", personality, debug=1)
mainpg.open()
mainpg.parse()


mainpg = mainpg.doRedirects() 
  
links = ["/~support/support.html"]
if not mainpg.containsLinks(links):
   print "Mainpage does not contain all the links it is supposed to do"
   sys.exit(1)

formpage = mainpg.click(links[0])
formpage = formpage.doRedirects()
if formpage.status != 200:
   print "Error loading subpage errorcode: " + str(formpage.status)
   sys.exit(1)

formpage.parse() # We need access to the form
#scorepage.printInfo()
# Get the form, and search for flag (if cookie is provided)
if oldflag != "":
   try:
	f = formpage.forms[0]
	f.fields["cc"] = oldflag 
	f.fields["amount"] = "555"
        if not "candidate" in f.fields:
           f.addField("candidate","")
        f.fields["candidate"] = "Stallone"

	resultingPage = f.click(None)
	resultingPage = resultingPage.doRedirects()
	data = resultingPage.page
	#print data
	
	start = data.find("Amount: ")
	if start < 0:
		print "Flag not found"
                oldflag = ""
	else:
		end   = data.find("<",start)
		oldamount = data[start+8:end]
		if int(oldamount)!=int(amount):
			oldflag = ""
   except Exception, e:
      print "Exception getting flag %s" % (e)

# Now create a new flag
amount = str(random.randint(0,10000))
newcookie =  newflag + ":" + amount
 
# The flag is set in the same form (image search)
try:
   f = formpage.forms[0]
   if not "candidate" in f.fields:
      f.addField("candidate","")
   f.fields["candidate"] = "Stallone"
   f.fields["cc"]     = newflag
   f.fields["amount"] = amount
   resultingPage = f.click(None)
   resultingPage = resultingPage.doRedirects()
   #print resultingPage.page
   if resultingPage.status != 200:
      print "Error setting new flag"
except Exception, e:
   print "Exception setting flag %s" % (e)

print "FLAG:" + oldflag
print "COOKIE:" + newcookie


