#!/usr/bin/env python
import sys
#import imp

from benign1 import Benign as Benign1
from benign2 import Benign as Benign2
from benign3 import Benign as Benign3
from benign4 import Benign as Benign4
from exploit import Exploit
from getflag import GetFlag
from setflag import SetFlag

HOST = '127.0.0.1'
PORT = 9898
FLAG = 'Victorymessage'

print 'Setflag..'
sf = SetFlag()
sf.execute(HOST, PORT, FLAG)
res = sf.result()
print 'Result: %s' % str(res)
flag_id = res['FLAG_ID']
cookie = res['COOKIE']
assert res['ERROR'] == 0

print 'Exploit..'
e = Exploit()
e.execute(HOST, PORT, flag_id)
print "Done exploiting"
res = e.result()
print 'Result: %s' % str(res)
assert res['FLAG'] == FLAG
assert res['ERROR'] == 0
###
###
print 'Getflag..'
cf = GetFlag()
cf.execute(HOST, PORT, flag_id, cookie)
res = cf.result()
print 'Result: %s' % str(res)
assert res['FLAG'] == FLAG
assert res['ERROR'] == 0
#
print 'Benign..'
b = Benign1()
b.execute(HOST, PORT)
res = b.result()
print 'Result: %s' % str(res)
assert res['ERROR'] == 0
#
b = Benign2()
b.execute(HOST, PORT)
res = b.result()
print 'Result: %s' % str(res)
assert res['ERROR'] == 0
#
b = Benign3()
b.execute(HOST, PORT)
res = b.result()
print 'Result: %s' % str(res)
assert res['ERROR'] == 0
#
b = Benign4()
b.execute(HOST, PORT)
res = b.result()
print 'Result: %s' % str(res)
assert res['ERROR'] == 0
