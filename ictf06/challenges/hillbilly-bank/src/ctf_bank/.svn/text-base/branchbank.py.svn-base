import Crypto.Hash.SHA
import Crypto.PublicKey.RSA
import pem
import random
import base64

class Bank:
   def __init__(self, pemfile):
      self.hash = Crypto.Hash.SHA.new()
      keyfile = pem.Keyfile(pemfile)
      if not keyfile.isPrivate():      
         self.key = Crypto.PublicKey.RSA.construct([keyfile.n, keyfile.e])
      else:
         raise Exception("Branch Bank needs public key")

   def validateCheck(self, check):
      unpacked =  base64.b64decode(check)
      decrypted = self.key.encrypt(unpacked, "")
      checkstr = decrypted[0]

      if len(checkstr) != 21 or not checkstr.isdigit():
         print "Invalid check"
         return None

      recipient = int(checkstr[:2])
      amount = int(checkstr[2:9])
      checknum = int(checkstr[9:])
      return (recipient, amount, checknum)
      

   def encodeIBAN(self, recipient, recipientaccount):
      ibanstr = "%02i%012i%012i" % (recipient, recipientaccount,random.randrange(0,999999999999))
      encrypted = self.key.encrypt(ibanstr, "")
      return base64.b64encode(encrypted[0])
