#!/usr/bin/python

import os, sys
import cgi
import pwd
import socket
import urlparse
import sys
import MySQLdb
from random import Random

db_host = "localhost"
db_acct = "contribute"
db_pass = "GoFuckYourself123"       # development password -- change me
db_db   = "Contributions"

def db_connect(db_host, db_acct, db_pass, db_db):

    try:
        conn = MySQLdb.connect (db_host,
                                db_acct,
                                db_pass,
                                db_db)
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    return conn

def process_contribution(conn, form):
    form_keys = form.keys()

    cursor = conn.cursor()

    rv = Random()
    rv.seed()
    id = int(rv.uniform(1,1e9))

    query = "INSERT INTO contributors (id, name, amount, address, ccn ) VALUES (%s, \"%s\", %s, \"%s\", \"%s\" ) ;" % ( id, form.getvalue("name"), form.getvalue("contribution"), form.getvalue("address"), form.getvalue("cc") )

    cursor.execute(query)
    conn.commit()

    print "Your contribution id is: %i. Please keep a copy of this number to access your contribution data in the future.<p>" % (id)

    cursor.close()

def main():

    print 'Content-type: text/html\n\n'

    print '<html><head>'
    print "<title>Thank You!</title>"
    print "<link href=\"spam.css\" rel=\"stylesheet\" type=\"text/css\" />"
    print "</head><body>"
    print "<h2> <i> Thank You! </i> </h2>"

    conn = db_connect(db_host, db_acct, db_pass, db_db)

    form = cgi.FieldStorage() 
                              

    process_contribution(conn, form)

    print "</body>"
    print "</html>"


if __name__ == '__main__':
    main()


