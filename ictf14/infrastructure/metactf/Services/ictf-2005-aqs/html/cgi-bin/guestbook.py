#!/usr/bin/python

from library import *

print "Content-type: text/html"
print

print """<html>
<head><title>The Book</title></head>
<body bgcolor="dddddd">
"""
if sign():
  signit()
else:
  thebook()
  print """<br><br>
          <table bgcolor="00ffff"><tr><td>
            <flash><font color="ffff00"><H2>Sign my guestbook</h2></font></flash>
            <form method="get" action="guestbook.py">Name:<input type="text" name="name"></input><br>
                               Comment:<input type="text" name="comment"></input><br>
                               Private:<input type="checkbox" name="priv"></input>
                               <input type="hidden" name="command" value="sign"></input><input type=submit></input>
             </form></td></tr>
          </table>
           <br><br>
          <table bgcolor="00ffff"><tr><td>
          <flash><font color="ffff00"><H2>Look up private entry</h2></font></flash>
            <form method="get" action="guestbook.py">Name:<input type="text" name="name"></input><br>
            <input type="hidden" name="command" value="lookup"></input><input type=submit></input></form>
          </td></tr>
          </table>
  """

print """
</body>
</html>"""
