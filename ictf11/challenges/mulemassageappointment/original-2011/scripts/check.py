import sys
import urllib
from itertools import izip, cycle

KEY="Dec 31"
CURRENT_FLAG="2tripleawesome"

def xor_crypt_string(data, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(data, cycle(key)))
try:
    flag=urllib.urlopen('http://localhost:8000/flag').read().split("message'>")[1].split("</div>")[0]
except:
    print "DOWN"
    sys.exit(1)
if xor_crypt_string(flag, KEY) == CURRENT_FLAG:
    print "OK"
