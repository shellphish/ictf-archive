#! /usr/bin/python

import os, random, sys, signal, popen2

thepid = 0

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def getRandomString(len):
	ret = ""
	for i in range(len):
		ret += random.choice(alphabet)
	return ret

def cleanup():
  if thepid != 0:
     os.kill(thepid, SIGTERM)
  sys.exit(1)

#### Main
sys.exit(1)
target   = sys.argv[1]
port     = 7413
newflag  = sys.argv[2]
if len(sys.argv) > 3:
	cookie = sys.argv[3]
	username = cookie
else:
	cookie = ""
	username = ""

oldflag = ""
 
signal.signal(signal.SIGTERM, cleanup)

if username != "":
   try:
        client = popen2.Popen3("./voteadmin --host %s --wwid %s --vote asfds"%(target,username))
	#client = os.popen("./voteadmin --host %s --wwid %s --vote asfds"%(target,username))
        thepid = client.pid
        stdout = client.fromchild 
	lines = stdout.readlines()
	stdout.close()

	oldflag = lines[1][19:-1]
	#print "OLD = %r"%oldflag
	#client.close()
   except Exception, e:
      print "Exception getting flag %s" % (e)

newuser   = getRandomString(8)
newcookie = newuser

try:
   client = popen2.Popen3("./voteadmin --host %s --wwid %s --vote %s"%(target,newuser,newflag))
   thepid = client.pid
   stdout = client.fromchild
   stdout.readlines()
   stdout.close()
except Exception, e:
   print "Exception setting flag %s" % (e)

print "\nFLAG:" + oldflag
print "COOKIE:" + newcookie
