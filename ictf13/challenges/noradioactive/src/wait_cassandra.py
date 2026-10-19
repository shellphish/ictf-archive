#!/usr/bin/env python
import pycassa
import time

db_hostname = 'localhost'
db_port = 9160


def check_cassandra():
	try:
		sysmgr = pycassa.system_manager.SystemManager("%s:%s" % (str(db_hostname), str(db_port)))
		return True
	except Exception:
		return False


while True:
	if check_cassandra() == True:
		break
	else:
		print "waiting for cassandra..."
	time.sleep(1)




