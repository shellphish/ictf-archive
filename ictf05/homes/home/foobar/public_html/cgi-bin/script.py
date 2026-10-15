#! /usr/bin/python
import cgi, sys, fcntl, os

print "Content-Type: text/html\n"
print
print '<html><head></head><body bgcolor="#6699ff" textcolor=white>'
print os.popen('id').readlines()
print '</body></html>'
