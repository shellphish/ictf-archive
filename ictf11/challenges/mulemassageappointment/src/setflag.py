import random
import rsa
import string
import urllib2
import urllib
PUBKEY="""-----BEGIN RSA PUBLIC KEY-----
MEgCQQDJ5O4F3O7eFlJVL0UOrENwU8omBWxqTc+ZPRZ11dIjMRowIB2iWCXq4a6k
YlcbynN/5/j1oXdFTMcYKq7R1D21AgMBAAE=
-----END RSA PUBLIC KEY-----"""

def randomstr(N=12):
  return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

class SetFlag():
  def execute(self, ip, port, flag):
    pubkey=rsa.PublicKey.load_pkcs1(PUBKEY)
    flag_id = randomstr()
    headers = {"msg": urllib.quote(rsa.encrypt(flag, pubkey)), "trackingid": urllib.quote(flag_id)}
    req = urllib2.Request("http://%s:%s/sendmessage" %(ip,port), None, headers)
    try:
        urllib2.urlopen(req)
    except Exception, e:
        print "Fail %s" % str(e)
    self.flag_id = flag_id
    self.token = "NOT_USED"
    self.error = 0
    self.error_msg = ""

  def result(self):
    return {'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }
