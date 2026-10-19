#!/usr/bin/env python
import sys

from benign2 import Benign
from leetexploit import Exploit
from getflag import GetFlag
from setflag import SetFlag

def get_random_string():
    import random
    import string
    return 'FLG' + ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(13))

HOST = '127.0.0.1'
PORT = 4444

FLAG = get_random_string()

flag_id = '213'
#print 'Setflag..'
#sf = SetFlag()
#sf.execute(HOST, PORT, FLAG)
#res = sf.result()
#print 'Result: %s' % str(res)
#flag_id = res['FLAG_ID']
#cookie = res['COOKIE']

print 'Exploit..'
e = Exploit()
e.execute(HOST, PORT, flag_id)
res = e.result()
print 'Result: %s' % str(res)
assert res['FLAG'] == FLAG

#print 'Getflag..'
#cf = GetFlag()
#cf.execute(HOST, PORT, flag_id, cookie)
#res = cf.result()
#print 'Result: %s' % str(res)
#assert res['FLAG'] == FLAG
#
#print 'Benign..'
#b = Benign()
#b.execute(HOST, PORT)
#res = b.result()
#print 'Result: %s' % str(res)
#assert res['ERROR'] == 0
