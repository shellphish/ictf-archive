#!/usr/bin/python

import os, random, time, sys, string, socket
 
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
good_password = ['bbbccc','aaabbb','cccddd']
bad_password  = ['table','desktop','message','password','robot']

rbuffer = ''
# ------------------------------------------------------------------

def readline(s):
	global rbuffer
	if '\n' in rbuffer:
		pos = rbuffer.find('\n')
		result = rbuffer[:pos]
		rbuffer = rbuffer[pos+1:]
		return result
	
	data = rbuffer+s.recv(100)
	while ('\n' in data) == False:
		data += s.recv(100)
	pos = data.find('\n');
	rbuffer = data[pos+1:]
	return data[:pos]
		

def read_flag(s, username, password):
	s.send('login %s %s\n'%(username,password))
	res = readline(s)
	print "Login %r"%res

	if res[:3] != "200":
		return ""

	s.send('stat\n')
	res = readline(s)
	print "Stat %r"%res
	if res[:5] == "There":
		return ""
	
	res = readline(s)
	flag = res[4:]
	
	while res[:3] != "200":
		print "*"+res
		res = readline(s)
	
	return flag
	
	
def create_flag(s, flag):
	username = random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet)
	password = random.choice(good_password)
	s.send('new %s %s\n'%(username,password))
	
	res = readline(s)
	print "RES1: %r"%res
	
	if res[:3] != "200":
		return ""
	
	s.send("to: xxxx\n")
	res = readline(s)
	print "TO: %r"%res
	
	s.send("spam\n")
	res = readline(s)
	res = readline(s)
	res = readline(s)
	print "SPAM: %r"%res
	
	s.send("%s\n"%flag)
	s.send(".\n")
	res = readline(s)
	print "END: %r"%res
	
	return username+":"+password
	
# ------------------------------------------------------------------
	
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((target, 4570))

res = readline(s)
res = readline(s)
res = readline(s)


if len(cookie) > 0:
	username, password = cookie.split(":")
	oldflag = read_flag(s,username,password)

cookie = create_flag(s,newflag)

s.send("exit\n")
s.close()

print "FLAG:%s"%oldflag
print "COOKIE:%s"%cookie
