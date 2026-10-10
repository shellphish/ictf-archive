from pyasn1.v1.type import univ
from pyasn1.v1.codec.der import decoder
import base64
import array

def longpack(l):
   bytes = array.array('B')
   while l != 0:
      bytes.append( l & 0xFF)
      l = l >> 8
   print "Bytecount %i" % len(bytes)
   return bytes.tostring()

def longunpack(s):
   ret = 0L
   bytes = array.array('B')
   bytes.fromstring(s)
   bytes.reverse()
   print "Bytecount2 %i" % len(bytes)
   for b in bytes:
      ret = ret << 8
      ret |= b
   return ret


class Keyfile:

   def __init__(self, filename):
      self.filename = filename
      lines = []
      f = file(filename)

      for line in f.readlines():
         if not line.startswith("--"):
           lines.append(line)
      encoded = base64.decodestring("".join(lines))
      decoded = decoder.decode(encoded)
      f.close()
      

      #print decoded[0]
      if decoded[0][0] == 0:
         #print "We have a private key"
         #print "n=%i" % long(decoded[0][1]) 
         #print "e=%i" % int(decoded[0][2])
         #print "d=%i" % long(decoded[0][3])
         self.n = long(decoded[0][1])
         self.e = long(decoded[0][2])
         self.d = long(decoded[0][3])
      else:
         #print "We have a public key"
         blob = encoded[22:]
         decoded = decoder.decode(blob)
         #print decoded

         #print "n=%i" % long(decoded[0][0]) 
         #print "e=%i" % int(decoded[0][1])
         self.n = long(decoded[0][0])
         self.e = long(decoded[0][1])
         self.d = None


   def isPrivate(self):
      return self.d != None
