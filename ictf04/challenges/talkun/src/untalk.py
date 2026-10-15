#!/usr/bin/python

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
        (username,password) = cookie.split(":")
else:
        cookie = ""
        username = ""
        password = ""

oldflag = ""

newuser = getRandomString(8)
newpass = getRandomString(8)

personality = browserpersonality.getRandomPersonality()

### Set flag
if 1 == 1:
#try:
   mainpg = pybrowse.Browser("http://"+ target  +":8081/", personality, debug=0);
   mainpg.open()
   mainpg = mainpg.doRedirects()
   mainpg.parse()
   #mainpg.printInfo()

   links = ["doc", "login", "note", "logout"]
   if not mainpg.containsLinks(links):
      print "Mainpage does not contain all the links it is supposed to do"
      sys.exit(1)

   testlink = random.choice(links)
   rpage = mainpg.click(testlink)
   rpage = rpage.doRedirects()
   if rpage.status != 200:
      print "Error loading subpage errorcode: " + str(rpage.status)
      sys.exit(1)

   loginpage = mainpg.click("login")
   loginpage = loginpage.doRedirects();
   loginpage.parse()
   #loginpage.printInfo()

   f = loginpage.forms[0]
   f.fields["username"] = newuser
   f.fields["password"] = newpass
   res = f.click(None)
   res = res.doRedirects()
   # Login OK page
   res.parse()
   #res.printInfo()
   res = res.click(res.links[0])
   res = res.doRedirects()
   # Submit note page
   res.parse()
   #res.printInfo()
   f = res.forms[0]
   f.fields["line"] = 1
   f.fields["character"] = 1
   f.fields["note"] = newflag
   res = f.click(None)
   res = res.doRedirects()
   if res.status != 200:
      print "Flag not accepted"
#except Exception, e:
#   print "Caught exception in setflag %s" %(e)

### Get flag  
if username != "":
  try:
     personality = browserpersonality.getRandomPersonality()
     mainpg = pybrowse.Browser("http://"+ target  +":8081/", personality, debug=0);
     mainpg.open()
     mainpg = mainpg.doRedirects()
     mainpg.parse()
     #mainpg.printInfo()

     notespage = mainpg.click("notes?username=" + username)
     notespage = notespage.doRedirects()
     searchpat = "\[" + username + ":([a-zA-Z0-9\/\+\=]*)\]"
     rs = re.search(searchpat, notespage.page)
     if rs and rs.group(1):
        oldflag =  rs.group(1)
     else:
        print notespage.page
        print "No flag found in page"

  except Exception, e:
     print "Caught exception in getflag %s" % (e)

print "FLAG:" + oldflag
print "COOKIE:" + newuser + ":" + newpass
