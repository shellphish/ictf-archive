#!/usr/bin/python
# Run as: python shof_bot.py 128.111.48.130:9180 new flag username:password
# The flag is used as the scorebot password

import httplib, os, random, time, sys, string, socket, urllib
 
target   = sys.argv[1]
newflag  = sys.argv[2]
port = 9180
target = target + ':' + str(port)
if len(sys.argv) > 3:
    cookie = sys.argv[3]
else:
    cookie = ""
oldflag  = ""
username = ""
password = ""

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

	
# ------------------------------------------------------------------
	
headers = {"Content-type": "application/x-www-form-urlencoded" }
if len(cookie) > 0:
    conn = httplib.HTTPConnection(target)
    email, password = cookie.split(":")
    vote = random.randint(1,1)
    params = urllib.urlencode({'email' : email, 'password' : password, 'vote' : vote})
    conn.request("POST", "/shof/vote", params, headers)
    r = conn.getresponse()
    data = r.read()
    if data.find('Your vote has been registered') >= 0:
        oldflag = password
    else:
        print 'Could not get flag', data
    conn.close();
		

username = random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet)

password = newflag
params = urllib.urlencode({'email' : username, 'password' : password, 'password_again' : password})
conn = httplib.HTTPConnection(target)
conn.request("POST", "/shof/register", params, headers)
r = conn.getresponse()
data = r.read()
if data.find('Welcome on board!') >= 0:
    pass
else:
    print 'Could not set flag', data

conn.close()

cookie = username+":"+password

print "FLAG:%s"%oldflag
print "COOKIE:%s"%cookie
