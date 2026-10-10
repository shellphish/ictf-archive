import Crypto.Hash.SHA
import Crypto.PublicKey.RSA
import pem
import random
import base64

SECRET = "Klrt1ZLnW6"

class Bank:
   def __init__(self, pemfile):
      self.hash = Crypto.Hash.SHA.new()
      keyfile = pem.Keyfile(pemfile)
      if keyfile.isPrivate():      
         self.key = Crypto.PublicKey.RSA.construct([keyfile.n, keyfile.e, keyfile.d])
      else:
         raise Exception("Central Bank needs private key")


   def makeCheck(self, recipient, amount):
      checkstr = "%02i%07i%012i" % (recipient, amount, random.randrange(0,999999999999))
      check = self.key.decrypt(checkstr)
      return  base64.b64encode(check)

   def createScorebotIBAN(self, team, round, amount):
      ibanstr = "%s%02i%04i%06i%04i" % (SECRET, team, round, amount, random.randrange(0,9999))
      encrypted = self.key.encrypt(ibanstr, "")
      return base64.b64encode(encrypted[0])

   def decodeIBAN(self, iban):
      blob =  base64.b64decode(iban)
      decrypted = self.key.decrypt(blob)

      if decrypted.startswith(SECRET):
         team =   int(decrypted[10:12])  
         round =  int(decrypted[12:16])
         amount = int(decrypted[16:22])
         return (team, round, amount)
      else:
         if len(decrypted) != 26 or not decrypted.isdigit():
            return None
         return int(decrypted[:2])
