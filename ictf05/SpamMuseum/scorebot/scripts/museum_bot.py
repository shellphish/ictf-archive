#!/usr/bin/python

import httplib, os, random, time, sys, string, socket, urllib
 
target   = sys.argv[1]
newflag  = sys.argv[2]
if len(sys.argv) > 3:
	cookie = sys.argv[3]
else:
	cookie = ""
oldflag  = ""
username = ""
password = ""

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

	
# ------------------------------------------------------------------
	
if len(cookie) > 0:
	conn = httplib.HTTPConnection(target)
	username, password = cookie.split(":")
	conn.request("GET", "/cgi-bin/museum_admin.pl?first=%s&last=%s&password=%s"%(username,password,"unbreakable"))
	r = conn.getresponse()
	data = r.read()
	print "=============\n     READ\n==============="
	print data
	pos = data.find("main")
	if pos>0:
		start = data.find(">",pos)
		end   = data.find("<",start)
		if start > 0 and end > 0:
			oldflag = data[start+1:end-1]
			oldflag = oldflag.strip() 
	conn.close();
		

username = random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet)

password = random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet)

conn = httplib.HTTPConnection(target)
conn.request("GET", "/cgi-bin/museum_upload.pl?first=%s&last=%s&idea=%s"%(username,password,urllib.quote(newflag)))
print "=============\n     READ\n==============="
r = conn.getresponse()
data = r.read()
print data

conn.close()

cookie = username+":"+password

print "FLAG:%s"%oldflag
print "COOKIE:%s"%cookie
