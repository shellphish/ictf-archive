#!/usr/bin/python

import centralbank
import pem
import sys

central = centralbank.Bank("ctf_bank/keys/private.pem")

recipient = int(sys.argv[1])
amount = int(sys.argv[2])
check = central.makeCheck(recipient, amount)
print "Check is %s" % check
