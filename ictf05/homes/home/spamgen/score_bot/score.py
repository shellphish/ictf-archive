#!/usr/bin/python

"""

https://<server>:4443/login? user=myname&password=miconsenta&operation=OP-store

this will "touch" the file "myname" and allow for the actual storing  of the flag which is done by

https://<server>:4443/store? filename=flagfile&content=flagcontent&user=myname

(note: the order of the parameters is IMPORTANT!)

To retrieve the file:

echo "flagfile" | nc -u <server> 2345

which will return

https://<server>:4443/flagfile
+flagcontent

"""

import pybrowse
import browserpersonality
import os, random, time, sys, string, re, socket, urllib

#service ports
httpPort = 80
udpPort   = 2345

#return values
retFlag   = ""
retCookie = ""

#constant form values
myPassword  = "miconsenta"
myOperation = "OP-store"

#timeout
udpResponseTimeout = 5

#name alphabet
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
           'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
           's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
           'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]

def getRandomString(len):
  ret = ""
  for i in range(len):
     ret += random.choice(alphabet)
  return ret



#MAIN
if len( sys.argv ) < 3:
 print "usage: %s <host> <flag> [<cookie>]" % ( sys.argv[0] )

myHost   = sys.argv[1]
myFlag   = sys.argv[2]
myCookie = ""

if len( sys.argv ) > 3:
 myCookie = sys.argv[3]

#get old flag
if myCookie != "":
 try:
   udpSocketDes = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
   udpSocketDes.connect( ( myHost, udpPort ) )
   udpSocketDes.settimeout( udpResponseTimeout )

   ( oldFileName, oldFlag ) = myCookie.split( ':' )

   sendString = oldFileName
   udpSocketDes.send( sendString )
   sendersAddr = ["", 0]
   while sendersAddr[0] != myHost:
     ( recvString, sendersAddr ) = udpSocketDes.recvfrom( 256 )

   #print recvString

   recvString = urllib.unquote( recvString )
   successPtr = recvString.find( oldFlag )
   if successPtr != -1:
     retFlag = oldFlag
   else:
     print "didn't find flag in return packet"
 except Exception, e:
   print "got exception %s getting flag" % ( e )
   #sys.exit( 1 )

#set the new flag
try:
 personality = browserpersonality.getRandomPersonality()
 mainpg = pybrowse.Browser("http://" + myHost + "/~spamgen/cgi-bin/spamgen.py?action=upload", personality, debug=0)
# mainpg = pybrowse.Browser("http://" + myHost + "/~spamgen/prova.html", personality, debug=0)
# mainpg = pybrowse.Browser("http://" + myHost + "/~spamgen/cgi-bin/prova.py", personality, debug=0)
 print "http://" + myHost + "/spamgen.py?action=upload"
 mainpg.open()
# mainpg = mainpg.doRedirects()
 mainpg.parse()
 randomName = getRandomString( 10 )
 mainpg.printInfo()
 adminForm = mainpg.forms[0]
 print "HELLO"
 adminForm.fields["user"]      = randomName
 adminForm.fields["pwd"]  = myPassword
 retCookie=randomName+':'+myPassword
 adminForm.fields["thetext"] = myFlag

 resultingPage = adminForm.click( None )
 resultingPage = resultingPage.doRedirects( )

 failPtr = resultingPage.page.find( "uccess" )

 if failPtr == -1:
   print "didn't find \"Update Successful\" in resulting page"
 else:
   successPtr = resultingPage.page.find( "Your file has been saved" )

except Exception, e:
 print "got exception %s setting new flag" % ( e )
 sys.exit( 1 )

print "FLAG:%s" % retFlag
print "COOKIE:%s" % retCookie
