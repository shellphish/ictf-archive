#!/usr/bin/python

import os, sys
import cgi
import pwd
import socket
import urlparse
import sys
import MySQLdb
import string

db_host = "localhost"
db_acct = "root"
db_pass = "ctftest"       # development password -- change me
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

def process_lookup(conn, form):
    form_keys = form.keys()

    cursor = conn.cursor()

    id = 1234;


    if "id" in form.keys():
        query = "SELECT * FROM contributors where id=%s ;" % ( form.getvalue("id") )
    else:
        if string.upper(form.getvalue("name")) == "NONE":
            return

        query = "SELECT * FROM contributors where name=\"%s\" ;" % ( form.getvalue("name") )

    cursor.execute(query)

    while (1):
        row = cursor.fetchone ()
        if row == None:
            break
        print "Contribution (id %s): %s, amount $%s.00, address=%s<p>" % (row[0], row[1], row[2], row[3] )

    cursor.close()

def main():

    print 'Content-type: text/html\n\n'

    print '<html><head>'
    print "<title>Thank you for joining our struggle</title>"
    print "<link href=\"/spam.css\" rel=\"stylesheet\" type=\"text/css\" />"
    print "</head><body>"
    print "<h2> <i> Your contributions </i> </h2>"

    print "</body>"
    print "</html>"

    conn = db_connect(db_host, db_acct, db_pass, db_db)

    form = cgi.FieldStorage()  
                               

    process_lookup(conn, form)

    print "</body>"
    print "</html>"


if __name__ == '__main__':
    main()





