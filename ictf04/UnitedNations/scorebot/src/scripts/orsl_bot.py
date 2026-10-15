#!/usr/bin/python

import httplib, os, random, time, sys, string, socket
 
target   = sys.argv[1]
newflag  = sys.argv[2]
if len(sys.argv) > 3:
	cookie = sys.argv[3]
else:
	cookie = ""
oldflag  = ""
username = ""
password = ""

alphabet = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B', 'C', 'D', 'E', 'F']

	
# ------------------------------------------------------------------
	
if len(cookie) > 0:
	conn = httplib.HTTPConnection(target)
	username = cookie
	conn.request("GET", "/acquire/get.php?ip=%s"%username)
	r = conn.getresponse()
	data = r.read()
	#print "=============\n     READ\n==============="
	#print data
	pos = data.find(",")
	if pos > 0:
		pos = data.find(",",pos+1)
		if pos > 0:
			end = data.find('\n',pos+1);
			oldflag = data[pos+1:end]
			conn.close();
		

username = ""
for x in range(32):
	username += random.choice(alphabet)

conn = httplib.HTTPConnection(target)
conn.request("GET", "/acquire/set.php?ip=%s&net=ucsb&de=%s"%(username,newflag))
#print "=============\n     READ\n==============="
r = conn.getresponse()
#data = r.read()
#print data

#conn.close()

cookie = username

print "FLAG:%s"%oldflag
print "COOKIE:%s"%cookie
