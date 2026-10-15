#!/usr/bin/env python

# IMPORTANT:
# This script requires the following packages: python-imaging and exiv2

import sys
from PIL import Image 
import ImageDraw, ImageFont
import random
import httplib
import os
import traceback

import ImageScripts.BaseScoringScript as scoringScript


#import os, sys - this snipit of code comes from the internets
#sys._getframe(1).f_code.co_filename == path of the module currently executing
#This code gets the path to the current executing module - where ever it is
#and does some path manipulation to let relative paths work in modules that
#could be executed from other locations

def execution_path(filename):
    return os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename)

class snitchScoringScript(scoringScript.BaseScoringScript):
    
    def post_multipart(self,host, selector, fields, files):
        content_type, body = self.encode_multipart_formdata(fields, files)
        h = httplib.HTTPConnection(host)  
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686;) Firefox/2.0.0.6',
            'Content-Type': content_type
            }
        h.request('POST', selector, body, headers)
        res = h.getresponse()
        return res.status, res.reason, res.read()    
    
    
    def encode_multipart_formdata(self,fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------8506126151759583858729434387'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
    
    def get_content_type(self,filename):
        return 'application/octet-stream'
    
    def doScoring(self):
        try: 
            # ------------------------- 
            # Retrieve old flag
            # ------------------------- 
        
            old_flag = "None"
            
            real_path = execution_path("./snitch_clean.jpg")
            save_path = execution_path("./%s.jpg"%self.teamIp)
            font_path = execution_path("arial.ttf")
           
            if self.cookie:
                name = self.cookie.replace("_"," ")
                img = Image.open(real_path)
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype(font_path, 20)
                draw.text(( 5, 40), name, fill="black", font=font)
                draw.text(( 5, 80), "abcde", fill="black", font=font)
                img.save(save_path)
        
                f = open(save_path)
                fdata = f.read()
                f.close()
        
                #print "Getting the flag..."
                status, reason, data = self.post_multipart(self.teamIp, "/~snitch/cgi-bin/snitch.py", [], [('paper',"%s"%save_path, fdata)])
        
                pos = data.find("thanks to paper")
                if pos == -1:
                    old_flag = "Nope"
                else:
                    old_flag = data[pos+21:][:self.getFlagSize()]
                
                self.validatePreviousFlag(old_flag)
        
            # ------------------------- 
            # Set the new one
            # ------------------------- 
            img = Image.open(real_path)
            draw = ImageDraw.Draw(img)
        
            first = self.getRandomString(random.randint(6,10))
            last = self.getRandomString(random.randint(6,10))
            name = first + " " + last
            
            address = "xxxxx" 
             
            #print "Generating picture..."
        
            font = ImageFont.truetype(font_path, 20)
            draw.text(( 5, 40), name, fill="black", font=font)
            draw.text(( 5, 80), address, fill="black", font=font)
        
            img.save(save_path)
        
            #print "Setting exif info..."
            os.popen("""exiv2 -M"set Exif.Photo.UserComment Paper_ID=%s" %s"""%(self.getNewFlagText(), save_path))
        
            f = open(save_path)
            fdata = f.read()
            f.close()
        
            #print "Setting flag..."
            status, reason, data = self.post_multipart(self.teamIp, "/~snitch/cgi-bin/snitch.py", [], [('paper', "%s"%save_path, fdata)])
            #print "Status ",status
        
            self.cookie = name.replace(" ","_")
            self.returnVal.setSuccess()
        
        except:
            traceback.print_exc(file=self.output) 
    
    def exerciseService(self):
        pass
        
def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return snitchScoringScript

