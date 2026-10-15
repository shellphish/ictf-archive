#!/usr/bin/python

"""
COOKIE == <username>:<password>:<flagname>



"""

import sys
import pybrowse
import browserpersonality

getFlagXml = """<?xml version="1.0"?>
<agent>
  <sender>
     <user>%s</user>
     <password>%s</password>
  </sender>
  <data>
     <item label="flagname">%s</item>
  </data>
  <code>
set name [data get flagname];
set flag [store get $name];
append result [results get] $flag;
results set $result;
  </code>
  <results>
     The flag is:
  </results>
</agent>
"""

setFlagXml = """<?xml version="1.0"?>
<agent>
  <sender>
     <user>%s</user>
     <password>%s</password>
  </sender>
  <data>
     <item label="flagname">%s</item>
     <item label="flagvalue">%s</item>
  </data>
  <code>
set flag [data get flagvalue];
set name [data get flagname];
store set $name $flag;
append result [results get] $name "=" $flag;
results set $result;
  </code>
  <results>
     The following flag has been set: 
  </results>
</agent>
"""


def printUsage( scriptName="" ):
  print "usage: %s <ip addr> <flag> [<cookie>]" % scriptName

def main( argv=None ):
  if argv == None:
    argv = sys.argv
  
  if len( argv ) < 3:
    printUsage( argv[0] )
  
  ipArg = argv[1]
  flagArg = argv[2]
  cookieArg = ""
  if len( argv ) > 3:
    cookieArg = argv[3]
  
  retFlag = ""
  retCookie = ""
  
  #attempt to log in and get old flag
  if cookieArg != "":
    try:
      ( oldUser, oldPass, oldFlagName ) = cookieArg.split( ":" )
      getRequest = getFlagXml % ( oldUser, oldPass, oldFlagName )
      #print getRequest
      
      personality = browserpersonality.getRandomPersonality( )
      mainpg = pybrowse.Browser( "http://" + ipArg + "/~spamagent/spamagent.html", personality, debug=0) 
      mainpg.open( )
      mainpg = mainpg.doRedirects( )
      mainpg.parse( )
    
      #print mainpg.page
      agentForm = mainpg.forms[0]
      #print "fields == %s" % ( str( agentForm.fields ) )
      agentForm.fields["script"] = getRequest
      outcomePage = agentForm.click( None )
      outcomePage.doRedirects( )
      
      rawPage = outcomePage.page
      
      print """-------- response to get flag --------
""" + rawPage + """
--------------------------------------"""
      
    except Exception, e:
      print "error retrieving flag! got: %s" % ( e )
  
  #set new flag and build cookie
  
  
  #return results
  print "FLAG:%s" % ( retFlag )
  print "COOKIE:%s" % ( retCookie )

if __name__ == "__main__":
  sys.exit( main( ) )