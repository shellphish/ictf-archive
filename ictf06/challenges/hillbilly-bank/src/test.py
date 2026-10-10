#!/usr/bin/python

import centralbank
import branchbank
import pem

### MAIN
central = centralbank.Bank("keys/private.pem")
branch = branchbank.Bank("keys/public.pem")


recipient = 99
amount = 10000
check = central.makeCheck(recipient, amount)
print "Check is [%s]" % check
print "Check validated as team %i amount %i checknumber %i" % branch.validateCheck(check)

print

iban = branch.encodeIBAN(12,9999)
print "IBAN is [%s]" % (iban)
iban_dec = central.decodeIBAN(iban)
if isinstance(iban_dec, int): 
   if iban_dec == None:
      print "Error, invalid IBAN"
   else:
      print "IBAN recipient is %i" % iban_dec
else:
   print "Error, regular IBAN decoded to a scorebot IBAN"

print 
scorebotiban = central.createScorebotIBAN(12,101,19978)
print "Scorebot IBAN is [%s]" % (scorebotiban)
decoded_iban = central.decodeIBAN(scorebotiban)
if not isinstance(decoded_iban, int):
   print "Decoded scorebotiban: Team: %i Round: %i Amount: %i" % (decoded_iban[0],decoded_iban[1],decoded_iban[2] )
else:
   if iban_dec == None:
      print "Error, invalid IBAN"
   else:
      print "Error, scorebot IBAN did not decode to a scorebot IBAN"

#kf = pem.Keyfile("keys/public.pem")
#kf2 = pem.Keyfile("keys/private.pem")
