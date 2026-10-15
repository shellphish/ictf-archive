import re, socket, sys

from ImageScripts.BaseScoringScript import BaseScoringScript 

seed = 0
r1 = re.compile("v[0-9]+\\.[0-9]+\\.([0-9]+)")
r2 = re.compile("[0-9a-f]+: ([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])")

"""
Get and set flag for syscalld.
"""

class SyscalldScoringScript(BaseScoringScript):
    
    def extractSeed(self,str):
        """
        Extract seed from banner string.
        """
    
        seed = 0
        m = r1.search(str)
        if m:
            seed = int(m.group(1))
            #print "DEBUG: seed=%d" % (seed)
        return seed
    
    def extractFlag(self,str):
        """
        Extract flag from "memory dump."
        """
        
        flag = ""
        lines = str.split("\n")
        for line in lines:
            m = r2.search(line)
            if m:
                #print "DEBUG: matched %s %s %s %s" % \
                #    (m.group(4), m.group(3), m.group(2), m.group(1))
                byte0 = int("0x" + m.group(4), 16)
                byte1 = int("0x" + m.group(3), 16)
                byte2 = int("0x" + m.group(2), 16)
                byte3 = int("0x" + m.group(1), 16)
                flag += chr(byte0) + chr(byte1) + chr(byte2) + chr(byte3)
    
        #print "DEBUG: flag=%s" % (flag)
    
        return flag
    
    def randomize(self,str):
        """
        Return "randomized" instruction.
        """
    
        global seed
    
        if seed <= 0:
            return str
    
        ret = ""
        for i in str:
            ret += chr(ord(i) ^ seed)
        
        #print "DEBUG: ret=%s" % (ret)
        return ret
    
    def send(self,fd, str):
        """
        Send string over socket.
        """
    
        #print "DEBUG: %s" % (str.strip())
        fd.send(str)
    
        return fd.recv(1024)
    
    def doScoring(self):
        """
        Main.
        """
        global seed
    
        oldFlag = ""
    
        try:
            # Connect
            fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fd.connect((self.teamIp,31337))
    
            # Read banner
            banner = fd.recv(1024)
    
            # XXX: Get seed
            seed = self.extractSeed(banner)
    
            # Open flag file
            self.send(fd, "%s %%ecx\n" % (self.randomize("pushl")))
            self.send(fd, "%s $0x5,%%eax\n" % (self.randomize("movl")))
            self.send(fd, "%s %%ecx,%%ebx\n" % (self.randomize("movl")))
            self.send(fd, "%s $0x7273752f,(%%ecx)\n" % (self.randomize("movl")))    # /usr
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x636f6c2f,(%%ecx)\n" % (self.randomize("movl")))    # /loc
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x732f6c61,(%%ecx)\n" % (self.randomize("movl")))    # al/s
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x65726168,(%%ecx)\n" % (self.randomize("movl")))    # hare
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x7379732f,(%%ecx)\n" % (self.randomize("movl")))    # /sys
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x6c6c6163,(%%ecx)\n" % (self.randomize("movl")))    # call
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x6c662f64,(%%ecx)\n" % (self.randomize("movl")))    # d/fl
            self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
            self.send(fd, "%s $0x00006761,(%%ecx)\n" % (self.randomize("movl")))    # ag..
            #send(fd, "%s $0x67616c66,(%%ecx)\n" % (randomize("movl")))
            #send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
            #send(fd, "%s $0x0,(%%ecx)\n" % (randomize("movl")))
            self.send(fd, "%s $0x42,%%ecx\n" % (self.randomize("movl")))
            self.send(fd, "%s $0x180,%%edx\n" % (self.randomize("movl")))
            #print send(fd, "%s\n" % (randomize("dump")))
            self.send(fd, "%s\n" % (self.randomize("sysenter")))
    
            #print send(fd, "%s\n" % (randomize("dump")))
    
            # Save fd in ebx, save buffer on stack
            self.send(fd, "%s %%eax,%%ebx\n" % (self.randomize("movl")))
            self.send(fd, "%s %%ecx\n" % (self.randomize("popl")))
            self.send(fd, "%s %%ecx\n" % (self.randomize("pushl")))
    
            #print send(fd, "%s\n" % (randomize("dump")))
    
            # Clear buffer
            #for i in range(8):
            #    send(fd, "%s $0x0,(%%ecx)\n" % (randomize("movl")))
            #    send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
            #send(fd, "%s %%ecx\n" % (randomize("popl")))
            #send(fd, "%s %%ecx\n" % (randomize("pushl")))
    
            # Get old flag
            self.send(fd, "%s $0x3,%%eax\n" % (self.randomize("movl")))
            self.send(fd, "%s $0x40,%%edx\n" % (self.randomize("movl")))
    
            #print send(fd, "%s\n" % (randomize("dump")))
    
            self.send(fd, "%s\n" % (self.randomize("sysenter")))
    
            #print send(fd, "%s\n" % (randomize("dump")))
            oldFlag = self.extractFlag(self.send(fd, "%s %%ecx\n" % (self.randomize("dump"))))
            self.validatePreviousFlag(oldFlag[:self.getFlagSize()])
            
            # Rewind file
            self.send(fd, "%s $0x13,%%eax\n" % (self.randomize("movl")))
            self.send(fd, "%s $0x0,%%ecx\n" % (self.randomize("movl")))
            self.send(fd, "%s $0x0,%%edx\n" % (self.randomize("movl")))
    
            self.send(fd, "%s\n" % (self.randomize("sysenter")))
    
            self.send(fd, "%s %%ecx\n" % (self.randomize("popl")))
            self.send(fd, "%s %%ecx\n" % (self.randomize("pushl")))
    
            # Write new flag
            newFlag = self.getNewFlagText()
            dword = ""
            for i in range(len(newFlag)):
                dword = "%2x%s" % (ord(newFlag[i]), dword)
                if i % 4 == 3:
                    self.send(fd, "%s $0x%s,(%%ecx)\n" % (self.randomize("movl"), dword))
                    self.send(fd, "%s $0x4,%%ecx\n" % (self.randomize("addl")))
                    dword = ""
    
            if dword:
                while len(dword) < 8:
                    dword = "00%s" % (dword)
                self.send(fd, "%s $0x%s,(%%ecx)\n" % (self.randomize("movl"), dword))
    
            self.send(fd, "%s $0x4,%%eax\n" % (self.randomize("movl")))
            self.send(fd, "%s %%ecx\n" % (self.randomize("popl")))
            self.send(fd, "%s %%ecx\n" % (self.randomize("pushl")))
            self.send(fd, "%s $0x%x,%%edx\n" % (self.randomize("movl"), len(newFlag)))
    
            self.send(fd, "%s\n" % (self.randomize("sysenter")))
            self.returnVal.setSuccess()
            
        except Exception, e:
            self.output.write("ERROR: %s" % (e))
            self.returnVal.setError()
    
    def exerciseService(self):
        pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return SyscalldScoringScript
