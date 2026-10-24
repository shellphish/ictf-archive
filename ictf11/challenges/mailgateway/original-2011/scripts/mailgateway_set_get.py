#!/usr/bin/env python

import logging
import random
import select
import socket
import string
import sys
import time

SOCKET_TIMEOUT = 15

def get_random_string(min, max):
    return ''.join(random.choice(string.letters) for i in range(min, max)) 

def get_random_email():
    tlds = ('com', 'org', 'info', 'biz')
    email = "%s@%s.%s" % (get_random_string(4,12), get_random_string(3,15), random.choice(tlds))
    return email

class MuleUser(object):
    PORT = 9119

    def __init__(self, ip):
        self.ip = ip

    def _connect(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((self.ip, MuleUser.PORT))
        self._s.settimeout(SOCKET_TIMEOUT)

        self._mailfd = self._s.makefile()

    def _send(self, data):
        self._s.sendall(data)

    def _readline(self):
        try:
            return self._mailfd.readline()
        except socket.error:
            return ''

    def _disconnect(self):
        try:
            self._s.close()
        except socket.error:
            pass

    def getFlag(self, cookie):
        logging.debug('checking the flag w/ cookie %s ...' % cookie)

        try:
            self._connect()
        except socket.error:
            logging.error("Email Aggregator is down: cannot read flag");
            return None

        try:
            account = cookie
            aggregator_msg="n%s|rq" % account
            self._send(aggregator_msg)
        except socket.error:
            logging.error('couldn\'t send the aggregator message: ' + aggregator_msg)
            return None

        flag = None
        while True:
            response = self._readline()
            if response == "":
                break
            parts = response.split()
            if len(parts) > 1:
                if parts[0] == "SUBJECT:":
                    flag = parts[1]

        self._disconnect()

        try:
            logging.debug('check successful: flag = ' + flag)
        except TypeError:
            logging.debug('server, y u have no flag?')
        return flag

    def setFlag(self, flag):
        logging.debug('setting the flag to ' + flag)

        sender = get_random_email()
        msgtime = time.strftime("%Y-%m-%d %H:%M:%S")
        msgbody = get_random_string(10, 100)

        account = get_random_string(8, 16)
        recipients = list()
        for i in range(random.choice(range(1, 2))):
            recipients.append(get_random_email())

        logging.debug("Account: [%s] Time: [%s]:  From: [%s] Subject: [%s] Body: [%s] Emails: [%s]" % (account, msgtime, sender, flag, msgbody, str(recipients)))

        try:
            self._connect()
        except socket.error:
            logging.error("Email Aggregator is down: cannot read flag");
            return None

        logging.debug("Creating account %s on mail gateway" % account)
        aggregator_msg = "TIME: %s\nFROM: %s\nSUBJECT: %s\nDATA: %s\n" % (msgtime, sender, flag, msgbody)
        aggregator_msg = "m%04d%s" % (len(aggregator_msg), aggregator_msg)
        aggregator_msg = "n%s|%s" % (account, aggregator_msg)
        for e in recipients:
            aggregator_msg = "%s+%s|" % (aggregator_msg, e)
            aggregator_msg = "%ssq" % aggregator_msg
        logging.debug("Sending compound email message: %s" % aggregator_msg)
        try:
            self._send(aggregator_msg)
        except socket.error:
            logging.error('couldn\'t send the aggregator message: ' + aggregator_msg)
            return None

        while True:
            response = self._readline()
            if response == "":
                break
            logging.debug("Received reply: %s" % response)

        self._disconnect()

        return account

def usage():
    print """
USAGE:
    get IP COOKIE
    check IP
"""

if __name__ == '__main__':
    try:
        _, operation, ip, data = sys.argv
    except ValueError:
        usage()
        sys.exit()

    user = MuleUser(ip)
    if operation == 'set':
        cookie = user.setFlag(data)
        if cookie is not None:
            print 'COOKIE:%s' % cookie
    elif operation == 'check':
        flag = user.getFlag(data)
        if flag is not None:
            print 'FLAG:%s' % flag
    else:
        usage()
