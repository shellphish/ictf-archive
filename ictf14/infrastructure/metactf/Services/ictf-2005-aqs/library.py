#!/usr/bin/python
import os
import random
import re
import os

parsepat = re.compile("The command is (.*)")
linepat = re.compile("^P. ([^ ]*) (.*)");
urlpat = re.compile("name=([^&]*)&comment=([^&]*)&(priv=)?")
urlpat2 = re.compile("name=([^&]*)&command=lookup")

alphabet = "abcdefghijklmnopqrstuvwxyz"

def getsession():
   res = ""
   for i in range(10):
      res = res + random.choice(alphabet)
   return res

def sign():
   for l in os.popen("./cgi-bin/cprog --process=\"<spamtron><exec-set><initializer>" + getsession() + "</initializer></exec-set></spamtron>\"").readlines():
     res = parsepat.match(l)
     if res:
        command = res.group(1)
        if command == "sign":
           return 1
   return None

def thebook():
  print """<table bgcolor="00ffff"><tr><td>
  <H1>Guestbook</H1>
  """
  res2 = urlpat2.match(os.environ["QUERY_STRING"])
  if res2:
    for l in os.popen("./cgi-bin/cprog --process=\"<spamtron><exec-set><showpriv>" + getsession() + "</showpriv></exec-set></spamtron>\"").readlines():
       res = linepat.match(l)
       if res and res.group(1) == res2.group(1):
          print "<b>" , res.group(1), "</b>: ", res.group(2), "<br>" 
  else:
    for l in os.popen("./cgi-bin/cprog --process=\"<spamtron><exec-set><showall>" + getsession() + "</showall></exec-set></spamtron>\"").readlines():
       res = linepat.match(l)
       if res:
          print "<b>" , res.group(1), "</b>: ", res.group(2), "<br>" 
  print """</td></tr></table>"""



def signit():
   res = urlpat.match(os.environ["QUERY_STRING"])
   if res:
      out = file("/var/ctf/aqs/guestbook", "a+")
      if res.group(3):
        out.write("PR " + res.group(1)+ " "+ res.group(2)+ "\n")
      else:
        out.write("PU "+ res.group(1)+ " "+ res.group(2)+ "\n")
      out.close()

   print """Thanks for signing my guestbook<br>
            <a href="guestbook.py">Go back</a>
"""

