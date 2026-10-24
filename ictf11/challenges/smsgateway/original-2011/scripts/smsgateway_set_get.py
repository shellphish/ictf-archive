#!/usr/bin/env python2.6
import sys
import os
import getopt
import socket
import threading
import select
import logging
import string
import signal
import xml.dom.minidom 
import MySQLdb
import struct
import binascii
import random
import time
import subprocess


def random_phonenumber():
    return "+1 (%s) %s-%s" %(random.randrange(100,999), random.randrange(100,999), random.randrange(1000,9999))

def random_fortune():
    return subprocess.check_output(['fortune', '-s']).strip()

def get_random_name(length):
    return random.choice(string.ascii_lowercase) + ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(length-1))

def get_random_sms(cookie, flag):
    carriers = ("T-Mobile", "Verizon", "AT&T", "Sprint") # Pick random among these
    msgtime = time.strftime("%Y-%m-%d %H:%M:%S")
    sender = cookie
    subject = flag
    msgbody = random_fortune()

    phone_numbers = list()
    for i in range(random.choice(range(1, 21))):
        phone_numbers.append("%s:%s" % (random.choice(carriers), random_phonenumber()))
    print "[%s]: From: [%s] Subject: [%s] Body: [%s] Phones: [%s]" % (msgtime, sender, subject, msgbody, str(phone_numbers))

    num_devices = len(phone_numbers)
    aggregator_msg = struct.pack("!I", len(msgtime)) + struct.pack("%ds" % len(msgtime), str(msgtime))
    aggregator_msg = aggregator_msg + struct.pack("!I", len(sender)) + struct.pack("%ds" % len(sender), str(sender))
    aggregator_msg = aggregator_msg + struct.pack("!I", len(subject)) + struct.pack("%ds" % len(subject), str(subject))
    aggregator_msg = aggregator_msg + struct.pack("!I", len(msgbody)) + struct.pack("%ds" % len(msgbody), str(msgbody))
    aggregator_msg = aggregator_msg + struct.pack("!I", num_devices)
    offset = 0
    i = 0
    phonelist = ""
    for device_descriptor in phone_numbers:
        aggregator_msg = aggregator_msg + struct.pack("!I", offset)
        phonelist = phonelist + struct.pack("!I", 0) + struct.pack("!I", len(device_descriptor)) + struct.pack("%ds" % len(device_descriptor), str(device_descriptor))
        offset = offset + 4 + 4 + len(device_descriptor)
        i = i + 1
    aggregator_msg = aggregator_msg + phonelist
    total_len = len(aggregator_msg)
    aggregator_msg = struct.pack("!I", total_len) + aggregator_msg
    return aggregator_msg

def send_sms(aggregator_msg, debug):
    if debug:
        print "Sending compound sms message: %s" % binascii.b2a_qp(aggregator_msg)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((service_host, service_port))
        smsfd = s.makefile()
        s.send(aggregator_msg)
        flag = ""
        while True:
            response = smsfd.readline().strip()
            if response == "":
                break;
            print "Received reply: %s" % response
            actual_response = response.split(":")[-1]
            if len(actual_response) > 0:
                flag = actual_response
        s.close()
    except Exception, err:
        print "SMS Aggregator is down";

    return flag



if __name__ == "__main__":
    debug = 1
    service_host = sys.argv[2]
    service_port = 1991

    if sys.argv[1] == "set":
        flag = sys.argv[3]
        cookie = get_random_name(6)
        sms = get_random_sms(cookie, flag)
        send_sms(sms,1)
        print "COOKIE:%s" % cookie
    elif sys.argv[1] == "check":
        cookie = sys.argv[3]
        sms = get_random_sms(cookie, "")
        flag = send_sms(sms,1)
        print "FLAG:%s" % flag
