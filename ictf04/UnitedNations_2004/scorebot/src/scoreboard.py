#!/usr/bin/python

import string
import cgi
import cgitb; cgitb.enable()
import os
import md5
import sys

gPassword = "f376966fbe97504612393f60418edce8"

statefilename="/ctf/var/scorebot.state"

class Tokenizer:
   def __init__(self,filename):
      self.f = file(filename, "r")
      self.state = "pre"
      self.token = ""   
      self.leftover = ""   

   def eat(self):
      if self.leftover != "":
         self.token = self.leftover
         self.leftover = ""
         return 1

      current = self.f.read(1);
      self.token = ""
      
      while current != "":
         if self.state == "pre":
            if current == '#':
	       self.state = "comment"
            elif current == '\"':
	       self.state = "quote"
            elif current == ';'  or current == '{' or current == '}':
	       self.token = current
	       return 1
            elif string.find(string.whitespace, current) == -1:
	       self.state = "txt"
	       self.token += current
            # Else whitespace, stay in pre

         elif self.state == "comment":
            if current == '\n':
               self.state = "pre"
            # Else stay in comment

         elif self.state == "quote":
            if current == '\"':
	       self.state = "pre"
               return 1
            elif current == '\\':
               self.state = "quote_escape"
            else:
               self.token += current

         elif self.state == "quote_escape":
            self.state = "quote";
            self.token += current;

         elif self.state == "txt":
            if current == '#' :
	       self.state = "comment"
	       return 1
            elif current == '\"':
	       self.state = "quote"
	       return 1
            elif current == ';'  or current == '{' or current == '}':
	       self.state = "pre"
	       self.leftover = current
	       return 1
            elif string.find(string.whitespace, current) != -1:
	       self.state = "pre"
	       return 1
            else:
               # Else non-space, stay in txt.
               self.token += current

         current = self.f.read(1);

      return 0

   def getToken(self):
      return self.token
  
   def close(self):
      self.f.close()


class Team:
   def __init__(self, name, total, trend, offense, defense, penalty):
      self.name = name
      self.total = total
      self.trend = trend
      self.offense = offense
      self.defense = defense
      self.penalty = penalty
      self.ownedcount = 0

def trend_compare(x,y):
   return y.trend - x.trend

def total_compare(x,y):
   return y.total - x.total

class Service:
   def __init__(self, name, round):
      self.name = name
      self.round = round

class Instance:
   def __init__(self,status,hackers):
      self.status = status
      self.hackers = hackers

class StateFile:
   def __init__(self, filename):
      self.filename = filename
      self.teams = []
      self.services = []
      self.instances = {}
      self.ownedcount = {}

   def parse(self):
      self.tok  = Tokenizer(statefilename)
      while self.tok.eat() == 1:
         token = self.tok.getToken()
         if token == "services":
            self.parseServices()
         elif token == "teams":
            self.parseTeams()
         elif token == "instances":
            self.parseInstances()
         else:
            raise Exception ("Parse error: unknown token " + token)
      self.tok.close()
      for i in range(1,len(self.teams)+1):
         if i in self.ownedcount:
            self.teams[i-1].ownedcount = self.ownedcount[i]
   
   def parseServices(self):
      if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
      if self.tok.getToken() != "{":
            raise Exception ("Expected {")
      if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")

      token = self.tok.getToken()
      while token != "}":
         servicename = token
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         round = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         if self.tok.getToken() != ";":
           raise Exception ("Expected ;")
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         token = self.tok.getToken()
         self.services.append(Service(servicename,round))

   def parseTeams(self):
      if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
      if self.tok.getToken() != "{":
            raise Exception ("Expected {")
      if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")

      token = self.tok.getToken()
      while token != "}":
         teamname = token
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         totalscore = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         trendscore = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         offensivescore = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         defensivescore = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         penaltyscore = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         lastpenalty = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         latestdiffscore = int(self.tok.getToken())
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         if self.tok.getToken() != ";":
            raise Exception ("Expected ;")
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         token = self.tok.getToken()
         self.teams.append(Team(teamname, totalscore, trendscore, offensivescore, defensivescore, penaltyscore))

   def parseInstances(self):
      if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
      if self.tok.getToken() != "{":
            raise Exception ("Expected {")
      if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")

      token = self.tok.getToken()
      while token != "}":
         teamname = token
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         servicename = self.tok.getToken()
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         status = self.tok.getToken()
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         cookie = self.tok.getToken()
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         hackers = self.tok.getToken()
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         perservicescore =  self.tok.getToken()       
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         maxedout =  self.tok.getToken()
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         if self.tok.getToken() != ";":
            raise Exception ("Expected ;")
         if self.tok.eat() == 0:
            raise Exception ("Unexpected EOF")
         token = self.tok.getToken()

         if not teamname in self.instances:
             self.instances[teamname] = {}
         self.instances[teamname][servicename] = Instance(status,hackers)
         
         hacks = hackers.split(",")
         for h in hacks:
            if h != "":
               if int(h) in self.ownedcount:
                  self.ownedcount[int(h)] += 1
               else:
                  self.ownedcount[int(h)] = 1


def printAdminScores(teams):
   teamcopy = [] + teams
   teamcopy.sort(total_compare)
   print """<table border>
<tr><th></th><th>Total Score</th><th>Trend Score</th>
<th>Offensive Score</th><th>Defensive Score</th><th>PenaltyScore</th></tr>
"""
   for t in teamcopy:
      print "<tr><th>" + t.name + "</th>"
      print "<td>" + str(t.total) + "</td>"
      print "<td>" + str(t.trend) + "</td>"
      print "<td>" + str(t.offense) + "</td>"
      print "<td>" + str(t.defense) + "</td>"
      print "<td>" + str(t.penalty) + "</td></tr>"
   print"</table>"

def printAdminStatus(teams, services, instances):
   print "<table border><tr><th></th>"
   for s in services:
      print "<th>" + s.name + "</th>"
   for t in teams:
      print "<tr><th>" + t.name + "</th>"
      for s in services:
         i = instances[t.name][s.name]
         print "<td>" + i.status + " " + i.hackers + "</td>"
      print "</tr>"
   print "<tr><th>Scoring Round</th>"
   for s in services:
      print "<td>" + str(s.round) + "</td>"
   print "</tr></table>"


def printScore(teams, services, instances, ownedcount):
   teamcopy = [] + teams
   teamcopy.sort(trend_compare)
   print "<table border><tr><th></th>"
   for s in services:
      print "<th>" + s.name + "</th>"
   print "<th>Trend Score</th><th>Own3d</th></tr>"
   teamnum = 0
   for t in teamcopy:
      teamnum += 1
      print "<tr><th>" + t.name + "</th>"
      for s in services:
         i = instances[t.name][s.name]
         print "<td>" + i.status  + "</td>"
      print "<td>" + str(t.trend) + "</td>"
      print "<td>" + str(t.ownedcount) + "</td>"
   print "<tr><th>Scoring Round</th>"
   for s in services:
      print "<td>" + str(s.round) + "</td>"
   print "<td></td><td></td></tr></table>"

def printLogin():
   print """
   <center><h1>Admin Login</h1></center>
   <form action="scoreboard.py?admin=1" method="post" >
   <p>Password
   <input type="password" name="pass" />
   <button type="submit">Login</button>
   </form>
   """


def printRedirect(url):
   print """Status: 301
Content-type: text/html
Location: """ + url + """

<HTML><HEAD><TITLE>Redirect</TITLE></HEAD>
<BODY><H2>You will be redirected</H2>
</BODY></HTML>"""
   

def validateAdmin(form):
   if not form.has_key("cookie"):
      if not form.has_key("pass"):
         printHeader()
         printLogin()
         printFooter()
         sys.exit(0)
      else:
         if md5.new(form.getvalue("pass","")).hexdigest() == gPassword:
           printRedirect("scoreboard.py?admin=1&cookie=" + md5.new(os.environ['REMOTE_ADDR'] + gPassword).hexdigest())      
           sys.exit(0)
         else:
           printHeader()
           #print(md5.new(form.getvalue("pass","")).hexdigest())
           printLogin()
           printFooter()
           sys.exit(0)
   else:
      if md5.new(os.environ['REMOTE_ADDR'] + gPassword).hexdigest() == form.getvalue("cookie",""):
         return 1
      else:
         return 0

   return 0

def printHeader():
   print """ContentType: text/html

<html>
<meta HTTP-EQUIV="refresh" CONTENT="10; ">
<head><title>CTF Scoreboard</title></head>
<body>"""

def printFooter():
   print "</body></html>"


# Main


form = cgi.FieldStorage()

is_admin = 0
if form.has_key("admin") or form.has_key("pass"):
   is_admin = validateAdmin(form)

printHeader()
sf = StateFile(statefilename)
sf.parse()

if is_admin == 1:
   printAdminScores(sf.teams)
   print "<br><br>"
   printAdminStatus(sf.teams, sf.services, sf.instances)
else:
   print """<center>
<h2>Scoreboard</h2>
"""
   printScore(sf.teams, sf.services, sf.instances, sf.ownedcount)

   print """<br><table><td>
<b>Trend Score:</b> An estimate of how well the team has been doing lately. Not the same as the total score.<br>
<b>Own3d:</b> How many services the team currently owns (has compromised)
</td></table><br>
<table><td>
<center><b>Statuscodes</b></center>
<b>up:</b> The service is up, it might be hacked by another team<br>
<b>down:</b> The service is not responding, no defensive score is awarded<br>
<b>wrong_flag:</b> The service responds, but the flag it provides is wrong.  No defensive score is awarded
</td></table><br>
<p><img src="/domo9-sm.jpg" width="400" height="300">
</center>
"""

printFooter()
