import sys
import os
import getopt
import socket
import threading
import select
import logging
import string
import signal
import libs
import xml.dom.minidom 
import MySQLdb
import struct
import binascii
import random

debug = 0

ERRPARAMS = 2
ERRSOCKET = 3
MYSQL_HOST = "muleserver";
MYSQL_DB = "mulemanager";
MYSQL_USER = "mulemanager";
MYSQL_PASSWORD = "grabthiswhileyoucan";
MESSAGE_DIR = "/home/msgdispatcher/messages"
SMS_AGGREGATOR_HOST = "localhost"
SMS_AGGREGATOR_PORT = 1991
EMAIL_AGGREGATOR_HOST = "localhost"
EMAIL_AGGREGATOR_PORT = 9119
COMMAND_DIR = "/home/msgdispatcher/commands"
extend = """libs.cleanup(COMMAND_DIR, words)"""

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
        
def usage(fname):
    print "%s [-d (debug)] -p <port>" % fname

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class ClientManager(threading.Thread):
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('dispatcher')
                
    def run(self):
        if debug:
            self.logger.debug("Thread manages client %s" % str(self.address))

        while True:
            try:
                infd = self.socket.makefile()
                msg = infd.readline().strip()
                words = string.split(msg)
                if words[0] == "STATUS":
                    ident = words[1]
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "r")
                    buf = f.read()
                    self.socket.send(buf)
                    self.socket.close()
                    return
                if words[0] == "SEND":
                    ident = words[1]
                    delim = words[2]
                    if debug:
                        self.logger.debug("Received command SEND [%s] [%s]" % (ident, delim))
                    buf = ''
                    complete = False
                    while True:
                        line = infd.readline()
                        if line == "":
                            break
                        if line.strip() == delim:
                            complete = True
                            break
                        buf = buf + line
                    if not complete:
                        self.logger.error("incomplete message")
                        self.socket.send("ERROR: incomplete message\n")
                        self.socket.close()
                        return
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "w+")
                    f.write("#RECEIVED\n")
                    f.close()
                    doc = xml.dom.minidom.parseString(buf)
                    if len(doc.getElementsByTagName("time")) == 0:
                        self.logger.error("incomplete message")
                        self.socket.send("ERROR: missing time\n")
                        self.socket.close()
                        return
                    msgtime = getText((doc.getElementsByTagName("time")[0]).childNodes)
                    if len(doc.getElementsByTagName("sender")) == 0:
                        self.logger.error("incomplete message")
                        self.socket.send("ERROR: missing sender\n")
                        self.socket.close()
                        return
                    sender = getText((doc.getElementsByTagName("sender")[0]).childNodes)
                    if len(doc.getElementsByTagName("group")) == 0:
                        self.logger.error("incomplete message")
                        self.socket.send("ERROR: missing group\n")
                        self.socket.close()
                        return
                    group = getText((doc.getElementsByTagName("group")[0]).childNodes)
                    if len(doc.getElementsByTagName("subject")) == 0:
                        self.logger.error("incomplete message")
                        self.socket.send("ERROR: missing subject\n")
                        self.socket.close()
                        return
                    subject = getText((doc.getElementsByTagName("subject")[0]).childNodes)
                    if len(doc.getElementsByTagName("msgbody")) == 0:
                        self.logger.error("incomplete message")
                        self.socket.send("ERROR: missing message body\n")
                        self.socket.close()
                        return
                    msgbody = getText((doc.getElementsByTagName("msgbody")[0]).childNodes)
                    if debug:
                        self.logger.debug("Parsed message time[%s] sender[%s] group[%s] subject[%s] body[%s]" % (msgtime, sender, group, subject, msgbody))
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "a+")
                    f.write("#PARSED %s\n" % subject)
                    f.close()
                    conn = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM groups_users WHERE groupname = %s", [group])
                    users = cursor.fetchall()
                    if debug:
                        self.logger.debug("Users: %s" % str(users))
                    if users == None or len(users) == 0:
                        self.logger.error("no recipients")
                        self.socket.send("ERROR: no recipients\n")
                        self.socket.close()
                        return
                    devices = list()
                    emails = list()
                    for u in users:
                        user = u[0]
                        cursor.execute("SELECT type, address, carrier, data FROM endpoints WHERE username = %s", [user])
                        while True:
                            endpoint = cursor.fetchone()
                            if endpoint == None:
                                break
                            endpoint_type = endpoint[0]
                            address = endpoint[1]
                            carrier = endpoint[2]
                            data = endpoint[3]
                            if endpoint_type == "sms":
                                devices.append((address, carrier))
                            elif endpoint_type == "email":
                                emails.append(address)
                    cursor.close()
                    conn.close()
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "a+")
                    f.write("FOUND ENDPOINTS\n")
                    f.close()
                    if debug:
                        self.logger.debug("Devices: %s" % str(devices))
                        self.logger.debug("Emails: %s" % str(emails))
                    num_devices = len(devices)
                    sms_status = "UNKNOWN\n"
                    if num_devices == 0:
                        sms_status = "SMS NOT PRESENT\n"
                    if num_devices > 0:
                        aggregator_msg = struct.pack("!I", len(msgtime)) + struct.pack("%ds" % len(msgtime), str(msgtime))
                        aggregator_msg = aggregator_msg + struct.pack("!I", len(sender)) + struct.pack("%ds" % len(sender), str(sender))
                        aggregator_msg = aggregator_msg + struct.pack("!I", len(subject)) + struct.pack("%ds" % len(subject), str(subject))
                        aggregator_msg = aggregator_msg + struct.pack("!I", len(msgbody)) + struct.pack("%ds" % len(msgbody), str(msgbody))
                        aggregator_msg = aggregator_msg + struct.pack("!I", num_devices)
                        offset = 0
                        i = 0
                        phonelist = ""
                        for d in devices:
                            aggregator_msg = aggregator_msg + struct.pack("!I", offset)
                            device_descriptor = "%s:%s" % (d[1], d[0])
                            phonelist = phonelist + struct.pack("!I", 0) + struct.pack("!I", len(device_descriptor)) + struct.pack("%ds" % len(device_descriptor), str(device_descriptor))
                            offset = offset + 4 + 4 + len(device_descriptor)
                            i = i + 1
                        aggregator_msg = aggregator_msg + phonelist
                        total_len = len(aggregator_msg)
                        aggregator_msg = struct.pack("!I", total_len) + aggregator_msg
                        if debug:
                            self.logger.debug("Sending compound sms message: %s" % binascii.b2a_qp(aggregator_msg))
                        sms_status = "SMS SENT\n"
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((SMS_AGGREGATOR_HOST, SMS_AGGREGATOR_PORT))
                            smsfd = s.makefile()
                            s.send(aggregator_msg)
                            response = smsfd.readline()
                            self.logger.debug("Received reply: %s" % response)
                            s.close()
                        except Exception, err:
                            self.logger.error("SMS Aggregator is down");
                            sms_status = "SMS FAILED\n"
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "a+")
                    f.write(sms_status)
                    f.close()

                    num_emails = len(emails)
                    email_status = "UNKNOWN\n"
                    if num_emails == 0:
                        email_status = "EMAILS NOT PRESENT\n"
                    if num_emails > 0:
                        account = ''.join(random.choice(string.letters) for i in range(4,12))
                        self.logger.debug("Creating account %s on mail gateway" % account)
                        aggregator_msg = "TIME: %s\nFROM: %s\nSUBJECT: %s\nDATA: %s\n" % (msgtime, sender, subject, msgbody)
                        aggregator_msg = "m%04d%s" % (len(aggregator_msg), aggregator_msg)
                        aggregator_msg = "n%s|%s" % (account, aggregator_msg)
                        for e in emails:
                            aggregator_msg = "%s+%s|" % (aggregator_msg, e)
                        aggregator_msg = "%ss" % aggregator_msg
                        if debug:
                            self.logger.debug("Sending compound email message: %s" % aggregator_msg)
                        email_status = "EMAIL SENT\n"
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((EMAIL_AGGREGATOR_HOST, EMAIL_AGGREGATOR_PORT))
                            mailfd = s.makefile()
                            s.send(aggregator_msg)
                            response = mailfd.readline()
                            self.logger.debug("Received reply: %s" % response)
                            s.close()
                        except Exception, err:
                            self.logger.error("Email Aggregator is down");
                            email_status = "EMAIL FAILED\n"
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "a+")
                    f.write(email_status)
                    f.close()
                    
                    self.socket.send("SUCCESS\n")
                    self.socket.close()
                    f = open("%s/%s" % (MESSAGE_DIR, ident), "a+")
                    f.write("COMPLETED\n")
                    f.close()
                    return
                else:
                    try:
                        eval(extend)
                    except ImportError:
                        self.socket.send("ERROR: unknown command\n")
                    self.socket.close()
                    return
            except Exception, err:
                self.logger.debug("Terminating (%s)..." % str(err))
                self.socket.send("Error: %s\n" % str(err))
                self.socket.close()
                break
        self.logger.debug("Exiting...")
        return  

def cleanup(signum, frame):
    global req_termination
    logger = logging.getLogger('dispatcher')
    logger.debug("Received %d. Cleaning up..." % signum)
    sys.exit(0)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    global debug

    port = 31337
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger('dispatcher')
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "dhp:")
        except getopt.error, msg:
            raise Usage(msg)
        for o, a in opts:
            if o == "-d":
                debug = 1
            if o == "-h":
                usage(os.path.basename(argv[0]))
                return 1
            if o == "-p":
                port = int(a)
    except Usage, err:
        logger.error("%s -- for help use -h" % err.msg)
        return ERRPARAMS

    if port == None:
        logger.error("Missing port number")
        usage(os.path.basename(argv[0]))
        return ERRPARAMS
    # Sets the signal
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    if debug:
        logger.debug("listening on port %d" % port)
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(("0.0.0.0", port))
        serversocket.listen(5)
    except Exception, err:
        logger.error("Cannot create socket on port %d: %s" % (port, str(err)))
        return ERRSOCKET
    
    while True:
        (clientsocket, address) = serversocket.accept()
        ct = ClientManager(clientsocket, address)
        ct.start()

def start():
    sys.exit(main())
