#!/usr/bin/python
import cgi

# debugging (comment out in production)
import cgitb; cgitb.enable()

import random
import os, sys 

import MySQLdb
from PIL import Image 
import ImageDraw
import subprocess 
import Cookie

from snitch_utils import *

pref = get_cookie()

print "Content-Type: text/html"
print set_cookie(pref) 
print ""

form = cgi.FieldStorage()
if not form.has_key("paper"): 
    print aboutus_page%"Send us a piece of paper <br> with the name and the address <br>and we'll take care of the rest. "
    sys.exit(0)	
	
img = Image.open("/home/snitch/public_html/boss.jpg")
db=MySQLdb.connect(user="snitch", passwd="snitch",db="snitch")
c=db.cursor()

piece_of_paper = form["paper"]
if piece_of_paper.file:
    filename = piece_of_paper.filename
    if filename[-3:] not in ["jpg", "tif", "png"]:
        print_page(img, ["We asked you for a piece of paper,","what is this stuff you sent us?"], pref)

    img_name = "/home/snitch/public_html/.tmp/%d"%(random.randint(10000000,99999999)) 

    if filename[-3:] == "tif":
        img_name+=".tif"
        f = open(img_name,"wb")
        f.write(piece_of_paper.value)
        f.close()
    else:
        try:
            im = Image.open(piece_of_paper.file)
        except:
            print_page(img, ["We asked you for a piece of paper,","what is this stuff you sent us?"], pref)

        if im.size[0] > 500 or im.size[1] > 500:
            print_page(img, ["I said a piece of paper,"," not a damn poster"], pref)
        img_name+=".bmp"
        im.save(img_name)

    text = img2txt(img_name, pref)
    paper_id = get_paper_id(piece_of_paper.value)
    
    if len(text) < 2:
        print_page(img, ["Write the name on the first line,","and the address on the second"], pref)
    text = [t.strip() for t in text]

    name = sanitize(text[0])
    addr = sanitize(text[1])    

    old_id = already_seized(text[0], c)
    if len(old_id) > 0:
        print_page(img, ["We already seized those computers", "thanks to paper n.%s"%(old_id,)], pref)

    add_to_the_book(name, addr, paper_id, c)
else:
    print_page(img, ["We asked you for a piece of paper,","what you think you are doing?"], pref)

print_page(img, [name[:30], "will receive a visit from our 'layers'"], pref)







