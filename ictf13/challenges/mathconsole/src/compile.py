#! /usr/bin/env python

import py_compile
import os
import sys

py_compile.compile("mathconsole.py")

if(len(sys.argv)>1):
    #anti unpickle trick: put the code at the end of this file at the start of your script
    fp = open("mathconsole.pyc","rb")
    c = fp.read()
    fp.close()

    off=-1
    for i in xrange(len(c)/2):
        b1 = c[i]
        if b1 == "\x15":
            for j in xrange(10):
                b2 = c[i+j*10]
                if b2 != "\x15":
                    break
            else:
                off = i
                break
        
    if(off==-1):
        print "NOT_FOUND"
    else:
        print "FOUND",off
        c2 = c[:off+1] + "\x00"  + c[off+2:]
        
    fp = open("mathconsole.pyc","wb")
    fp.write(c2)
    fp.close()
    print "PATCHED"
    
'''
fff=False
if(fff):
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
'''
