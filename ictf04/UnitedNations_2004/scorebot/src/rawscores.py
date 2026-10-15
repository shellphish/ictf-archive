#!/usr/bin/python

import string
import cgi
import cgitb; cgitb.enable()
import os
import md5
import sys

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
   return y.trend - x.trend

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


def printScore(teams, services, instances):
   teamcopy = [] + teams
   teamcopy.sort(trend_compare)
   sys.stdout.write("|")
   for s in services:
      sys.stdout.write(s.name + "|")
   print

   for t in teamcopy:
      sys.stdout.write("|" + t.name + "|")
      for s in services:
         i = instances[t.name][s.name]
         sys.stdout.write(i.status +" ")
      sys.stdout.write("|" + str(t.trend) + "|" + str(t.ownedcount) +"|")
      print

def printHeader():
   print "ContentType: text/plain\n"

# Main


form = cgi.FieldStorage()

#if not form.has_key("pass"):
#   sys.exit(0)

printHeader()
sf = StateFile(statefilename)
sf.parse()
printScore(sf.teams, sf.services, sf.instances)

