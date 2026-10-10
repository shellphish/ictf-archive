import time
import random
import string
import sqlite
import sys
import traceback
import os

sec_deposit = 1000

class CreditCard:
	def __init__(self, row, db):
		self.card = row[0] # It is a number
		self.iban = sqlite.decode(row[4])
		self.tobecommitted = 0
		self.db = db
		self.sec_deposit = sec_deposit
		
		try:
			cu = db.cursor()
			cu.execute("select * from CREDIT where card_no = %d"%self.card)
			row = cu.fetchone()
			expiration = int(row[1])+600
			self.sec_deposit = int(row[2])
			self.current = int(row[3])
				
			# If the test time is over, give him back the security deposit
			if time.time() > expiration:
				self.R_submit(sec_deposit)
		except:
			print "error reading the database"
		
	def movements(self):
		res = []
		cu = self.db.cursor()
		cu.execute('select * from MOVS where card_no == %d'%self.card)
		for row in cu.fetchall():
			if row[2] > 0:
				res.append([row[0], "deposit", row[2]])
			else:
				res.append([row[0], "withdrawal", abs(row[2])])
		return res		

	def withdrawal(self, amount):
		cu = self.db.cursor()
		if amount > 0:
			amount = amount * -1
		cu.execute('insert into MOVS values(%d, %d, %d)'%(int(time.time()), self.card, amount))
		self.db.commit()
		return "Fetch the money in 30 seconds... "
	
	def pay(self, amount):
		if (amount + self.current) > self.sec_deposit:
			return -1

		self.current += amount
		cu = self.db.cursor()
		cu.execute("update CREDIT set current_credit = %d where card_no = %d"%(self.current, self.card))
		self.db.commit()
		return amount		

	def close(self):
		self.R_submit(self.sec_deposit)
		cu = self.db.cursor()
		cu.execute("delete from CREDIT where card_no = %d"%self.card)
		cu.execute("delete from CARDS where card_no = %d"%self.card)
		cu.execute("delete from MOVS where card_no = %d"%self.card)
		self.db.commit()
		return self.sec_deposit
	
	# Restrincted command (cannot be invoked from outside)
	def R_submit(self, amount):
		name = random.randint(0,9999)
		f = open("/var/spool/transactions/atm/%d"%name,'w')
		f.write("%d %s"%(amount, self.iban))
		f.close()
	
	# Restrincted command (cannot be invoked from outside)
	def R_add_to_movements(self, amount):
		cu = self.db.cursor()
		cu.execute('insert into MOVS values(%d, %d, %d)'%(int(time.time()), self.card, amount))
		self.db.committ()
		

class DebitCard:
	def __init__(self, row, db):
		self.card = row[0] # It is a number
		self.iban = sqlite.decode(row[4])
		self.tobecommitted = 0
		self.db = db
		
	def deposit_check(self, check):
		if len(check) != 172:
			return -1
		value = self.R_get_check_value(check)
		if value > 0:
			self.tobecommitted += value
			return value
		return -1

	def movements(self):
		res = []
		cu = self.db.cursor()
		cu.execute('select * from MOVS where card_no == %d'%self.card)
		for row in cu.fetchall():
			if row[2] > 0:
				res.append([row[0], "deposit", row[2]])
			else:
				res.append([row[0], "withdrawal", abs(row[2])])
		return res		

	def commit(self):
		try:
			tmp = self.tobecommitted
			self.R_submit(self.tobecommitted)
			self.tobecommitted = 0
		except:
			pass
		return tmp

	def close(self):
		cu = self.db.cursor()
		cu.execute("delete from CARDS where card_no = %d"%self.card)
		cu.execute("delete from MOVS where card_no = %d"%self.card)
		self.db.commit()
		return 1
	
	def withdrawal(self, amount):
		cu = self.db.cursor()
		if amount > 0:
			amount = amount * -1
		cu.execute('insert into MOVS values(%d, %d, %d)'%(int(time.time()), self.card, amount))
		self.db.commit()
		return "Fetch the money in 30 seconds... "
	
	# Restrincted command (cannot be invoked from outside)
	def R_submit(self, amount):
		name = random.randint(0,9999)
		f = open("/var/spool/transactions/atm/%d"%name,'w')
		f.write("%d %s"%(amount, self.iban))
		f.close()
		self.R_add_to_movements(amount)
		
	
	# Restrincted command (cannot be invoked from outside)
	def R_get_check_value(self, check):
		# no command injection
		if check.find(";") != -1: 
			return -1
		proc = os.popen("/usr/bin/ccheck %s"%check)
		try:
			res = proc.readline()
			#print res
			res = int(res)
		except:
			return -1
		return res
	
	# Restrincted command (cannot be invoked from outside)
	def R_add_to_movements(self, amount):
		cu = self.db.cursor()
		cu.execute('insert into MOVS values(%d, %d, %d)'%(int(time.time()), self.card, amount))
		self.db.committ()
		
class ATM:
	def __init__(self):
		self.users_in = {}
		try:
			self.db   = sqlite.connect("/home/atm/atmdb")
		except:
			sys.exit(-1)
		
	def getTimeStamp(self):
		print "TIMESTAMP"
        	return time.time()
	
	# Request an electronic ATM card
	def request_dcard(self, firstname, lastname, account_number):
		print "REQUEST DCARD"
		try:
			cu = self.db.cursor()
			card = random.randint(100000000,999999999)
			pin  = random.randint(1000,9999)
			query = 'insert into CARDS values(%d, "%s", "%s", %d, "%s")'%(
			  card, 
			  sqlite.encode(firstname), 
			  sqlite.encode(lastname), 
			  pin, 
			  sqlite.encode(account_number))
			#print query
			cu.execute(query)
			self.db.commit()
		except:
			traceback.print_exc(file=sys.stdout)
			return -1
		return "%d@D%d"%(pin,card)
	

	# Request an electronic ATM/Credit card
	# Requires a check of 1000 Dollars
	def request_ccard(self, firstname, lastname, account_number, check):
		print "REQUEST CCARD"
		if check.find(";") != -1: 
			return -1
		res = os.popen("/usr/bin/ccheck %s"%check)
		res = int(res.readline())
		if (res < sec_deposit):
			return -1		
		try:
			cu = self.db.cursor()
			card = random.randint(100000000,999999999)
			pin  = random.randint(1000,9999)
			query = 'insert into CARDS values(%d, "%s", "%s", %d, "%s")'%(
			  card, 
			  sqlite.encode(firstname), 
			  sqlite.encode(lastname), 
			  pin, 
			  sqlite.encode(account_number))
			cu.execute(query)
			query = 'insert into CREDIT values(%d, %d, %d, %d)'%(
			  card, 
			  int(time.time()), 
			  res, 0)
			cu.execute(query)
			self.db.commit()
		except:
			traceback.print_exc(file=sys.stdout)
			return "-1 (error)"
		return "%d@C%d"%(pin,card)
			
	# Load an account
	def load_account(self, auth):
		print "LOAD ACCOUNT"
		try:
			pin, card = auth.split("@")
			pin = int(pin)
			type = card[0]
			card = int(card[1:])
			cu = self.db.cursor()
			cu.execute('select * from CARDS where pin == %d and card_no == %d'%(pin,card))
			row = cu.fetchone()
			if row != None:
				if type == 'C':
					return CreditCard(row, self.db)
				elif type == 'D':
					return DebitCard(row, self.db )
				else:
					return None
		except:
			traceback.print_exc(file=sys.stdout)
		 	return None	
		return None
		
	def cmd(self, accn, cmdname, *cmdparams):
		print "CMD: %s"%cmdname
		if self.users_in.has_key(accn) == False:
			return -1
		obj = self.users_in[accn]
		if (cmdname[0]=='R'):
			return -1
		args = [str(x) for x in cmdparams]
		#print args
		res = eval("obj.%s(%s)"%(cmdname, string.join(args,",")))
		return res
											 
	def gen_accn(self):
		return random.randint(1000000,99999999) 
		
	def login(self, auth):
		print "LOGIN"
		acc = None
		res = 0
		if auth.find("@") != -1:
		    	acc = self.load_account(auth)
			if acc == None:
				return 0
		    	res = self.gen_accn()
		    	self.users_in[res]=acc
		    	return res
		else:
			return -1
			
	def logout(self, accn):
		print "LOGOUT"
		del self.users_in[accn]

	def num(self):
		return len(self.users_in)
	
		  
