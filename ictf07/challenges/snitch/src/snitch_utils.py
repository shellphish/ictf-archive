#!/usr/bin/python
import cgi
# debugging
import cgitb; cgitb.enable()
import random
import os, sys 

import Cookie

import MySQLdb
from PIL import Image 
import ImageDraw
import subprocess 

page = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    
    <meta name="Generator" content="iWeb 2.0.2" />
    <meta name="iWeb-Build" content="local-build-20071202" />
    <meta name="viewport" content="width=700" />
    <title>THE MAFIA
Music and Film Industry Association</title>
    <link rel="stylesheet" type="text/css" media="screen,print" href="/Site/About_us_files/About_us.css" />
    <!--[if IE]><link rel='stylesheet' type='text/css' media='screen,print' href='/Site/About_us_files/About_usIE.css'/><![endif]--><style type="text/css">
/*<![CDATA[*/
	@import "/Site/Scripts/Widgets/HTMLRegion/Paste.css";
/*]]>*/
</style>
    <script type="text/javascript" src="/Site/Scripts/iWebSite.js"></script>
    <script type="text/javascript" src="/Site/Scripts/Widgets/SharedResources/WidgetCommon.js"></script>
    <script type="text/javascript" src="/Site/Scripts/Widgets/Navbar/navbar.js"></script>
    <script type="text/javascript" src="/Site/Scripts/iWebImage.js"></script>
    <script type="text/javascript" src="/Site/Scripts/Widgets/HTMLRegion/Paste.js"></script>
    <script type="text/javascript" src="/Site/About_us_files/About_us.js"></script>
  </head>
  <body style="background: #131010; margin: 0pt; " onload="onPageLoad();" onunload="onPageUnload();">
    <div style="text-align: center; ">
      <div style="margin-bottom: 0px; margin-left: auto; margin-right: auto; margin-top: 0px; overflow: hidden; position: relative; word-wrap: break-word;  text-align: left; width: 700px; " id="body_content">
        <div style="background: transparent url(/Site/About_us_files/rpamtile_v6.jpg) repeat scroll top left; width: 700px; ">
          <div style="height: 141px; margin-left: 0px; position: relative; width: 700px; z-index: 10; " id="header_layer">
            <div style="height: 0px; line-height: 0px;" class="bumper">
	</div>
            <div style="height: 139px; width: 636px;  height: 139px; left: 33px; position: absolute; top: 2px; width: 635px; z-index: 1; " class="tinyText">
              <div style="position: relative; width: 635px; ">
                <img src="/Site/About_us_files/shapeimage_1.png" alt="" style="height: 107px; left: 0px; margin-left: -1px; margin-top: 24px; position: absolute; top: 0px; width: 471px; " />
              </div>
            </div>
          </div>
          <div style="margin-left: 0px; position: relative; width: 700px; z-index: 0; " id="nav_layer">
            <div style="height: 0px; line-height: 0px;" class="bumper">
	</div>
            <div style="height: 490px; width: 700px;  height: 490px; left: 0px; position: absolute; top: -489px; width: 700px; z-index: 1; " class="tinyText style_SkipStroke">
              <img src="/Site/About_us_files/navfill-v2.jpg" alt="" style="border: none; height: 490px; width: 700px; " />
            </div>
            <div style="height: 1px; line-height: 1px;" class="tinyText"></div>
            <div class="com-apple-iweb-widget-navbar flowDefining" id="widget0" style="margin-left: 0px; margin-top: -1px; position: relative; width: 700px; z-index: 1; ">
    
              <div id="widget0-navbar" class="navbar">

      
                <div id="widget0-bg" class="navbar-bg">

        
                  <ul id="widget0-navbar-list" class="navbar-list">
 <li></li> 
</ul>
                  
      
</div>
                
    
</div>
            </div>
            <script type="text/javascript"><!--//--><![CDATA[//><!--
new NavBar('widget0', '/Site/Scripts/Widgets/Navbar', '/Site/Scripts/Widgets/SharedResources', '.', {"current-page-GUID": "304FFF51-50E7-4F41-B87F-D0E5FEDEA678", "path-to-root": "", "isCollectionPage": "NO", "navbar-css": ".navbar {\n\tfont-family: 'Courier New', Courier, monospace, serif;\n\tfont-size: 1.1em;\n\tcolor: #AFAA9F;\n\tmargin: -2px 0 0 0px;\n\tline-height: 20px;\n\tpadding: 5px 0 12px 0;\n\tfont-weight: bold;\n\tbackground-image: url(/Site/About_us_files\/navfill-v2_1.jpg);\n}\n\n.navbar-bg {\n\ttext-align: left;\n}\n\n.navbar-bg ul {\n\tlist-style: none;\n\tmargin: 0px;\n\tpadding: 0 10px 0 30px;\n}\n\n\nli {\n\tlist-style-type: none;\n\tdisplay: inline;\n\tpadding: 0px 25px 0 0;\n}\n\n\nli a {\n\ttext-decoration: none;\n\tcolor: #AFAA9F;\n}\n\nli a:visited {\n\ttext-decoration: none;\n\tcolor: #AFAA9F;\n}\n\nli a:hover\n{\n \tcolor: #D64600;\n}\n\n\nli.current-page a\n{\n\t color: #fff;\n\n}\n"});
//--><!]]></script>
           <div style="clear: both; height: 0px; line-height: 0px;" class="spacer"></div>
          </div>
          <div style="margin-left: 0px; position: relative; width: 700px; z-index: 5; " id="body_layer">
            <div style="height: 0px; line-height: 0px;" class="bumper"></div>
            <div style="height: 25px; width: 700px;  height: 25px; left: 0px; position: absolute; top: -15px; width: 700px; z-index: 1; " class="tinyText style_SkipStroke">
              <img src="/Site/About_us_files/pagetop10.png" alt="" style="border: none; height: 25px; width: 700px; " />
            </div>
<br><br><center>
	%s
</center>
<br><br>
         </div>
        </div>
      </div>
    </div>
  </body>
</html>

"""

aboutus_page = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    
    <meta name="Generator" content="iWeb 2.0.2" />
    <meta name="iWeb-Build" content="local-build-20071202" />
    <meta name="viewport" content="width=700" />
    <title>THE MAFIA
Music and Film Industry Association</title>
    <link rel="stylesheet" type="text/css" media="screen,print" href="/Site/About_us_files/About_us.css" />
    <!--[if IE]><link rel='stylesheet' type='text/css' media='screen,print' href='/Site/About_us_files/About_usIE.css'/><![endif]--><style type="text/css">
/*<![CDATA[*/
	@import "/Site/Scripts/Widgets/HTMLRegion/Paste.css";
/*]]>*/
</style>
    <script type="text/javascript" src="/Site/Scripts/iWebSite.js"></script>
    <script type="text/javascript" src="/Site/Scripts/Widgets/SharedResources/WidgetCommon.js"></script>
    <script type="text/javascript" src="/Site/Scripts/Widgets/Navbar/navbar.js"></script>
    <script type="text/javascript" src="/Site/Scripts/iWebImage.js"></script>
    <script type="text/javascript" src="/Site/Scripts/Widgets/HTMLRegion/Paste.js"></script>
    <script type="text/javascript" src="/Site/About_us_files/About_us.js"></script>
  </head>
  <body style="background: #131010; margin: 0pt; " onload="onPageLoad();" onunload="onPageUnload();">
    <div style="text-align: center; ">
      <div style="margin-bottom: 0px; margin-left: auto; margin-right: auto; margin-top: 0px; overflow: hidden; position: relative; word-wrap: break-word;  text-align: left; width: 700px; " id="body_content">
        <div style="background: transparent url(/Site/About_us_files/rpamtile_v6.jpg) repeat scroll top left; width: 700px; ">
          <div style="height: 141px; margin-left: 0px; position: relative; width: 700px; z-index: 10; " id="header_layer">
            <div style="height: 0px; line-height: 0px;" class="bumper">
	</div>

            <div style="height: 139px; width: 636px;  height: 139px; left: 33px; position: absolute; top: 2px; width: 635px; z-index: 1; " class="tinyText">
              <div style="position: relative; width: 635px; ">
                <img src="/Site/About_us_files/shapeimage_1.png" alt="" style="height: 107px; left: 0px; margin-left: -1px; margin-top: 24px; position: absolute; top: 0px; width: 471px; " />
              </div>
            </div>
          </div>
          <div style="margin-left: 0px; position: relative; width: 700px; z-index: 0; " id="nav_layer">
            <div style="height: 0px; line-height: 0px;" class="bumper">
	</div>
            <div style="height: 490px; width: 700px;  height: 490px; left: 0px; position: absolute; top: -489px; width: 700px; z-index: 1; " class="tinyText style_SkipStroke">
              <img src="/Site/About_us_files/navfill-v2.jpg" alt="" style="border: none; height: 490px; width: 700px; " />
            </div>
            <div style="height: 1px; line-height: 1px;" class="tinyText"></div>
            <div class="com-apple-iweb-widget-navbar flowDefining" id="widget0" style="margin-left: 0px; margin-top: -1px; position: relative; width: 700px; z-index: 1; ">
    
              <div id="widget0-navbar" class="navbar">

      
                <div id="widget0-bg" class="navbar-bg">

        
                  <ul id="widget0-navbar-list" class="navbar-list">
 <li></li> 
</ul>
                  
      
</div>
                
    
</div>
            </div>
            <script type="text/javascript"><!--//--><![CDATA[//><!--
new NavBar('widget0', '/Site/Scripts/Widgets/Navbar', '/Site/Scripts/Widgets/SharedResources', '.', {"current-page-GUID": "304FFF51-50E7-4F41-B87F-D0E5FEDEA678", "path-to-root": "", "isCollectionPage": "NO", "navbar-css": ".navbar {\n\tfont-family: 'Courier New', Courier, monospace, serif;\n\tfont-size: 1.1em;\n\tcolor: #AFAA9F;\n\tmargin: -2px 0 0 0px;\n\tline-height: 20px;\n\tpadding: 5px 0 12px 0;\n\tfont-weight: bold;\n\tbackground-image: url(/Site/About_us_files\/navfill-v2_1.jpg);\n}\n\n.navbar-bg {\n\ttext-align: left;\n}\n\n.navbar-bg ul {\n\tlist-style: none;\n\tmargin: 0px;\n\tpadding: 0 10px 0 30px;\n}\n\n\nli {\n\tlist-style-type: none;\n\tdisplay: inline;\n\tpadding: 0px 25px 0 0;\n}\n\n\nli a {\n\ttext-decoration: none;\n\tcolor: #AFAA9F;\n}\n\nli a:visited {\n\ttext-decoration: none;\n\tcolor: #AFAA9F;\n}\n\nli a:hover\n{\n \tcolor: #D64600;\n}\n\n\nli.current-page a\n{\n\t color: #fff;\n\n}\n"});
//--><!]]></script>
           <div style="clear: both; height: 0px; line-height: 0px;" class="spacer"></div>
          </div>
          <div style="margin-left: 0px; position: relative; width: 700px; z-index: 5; " id="body_layer">
            <div style="height: 0px; line-height: 0px;" class="bumper"></div>
            <div style="height: 25px; width: 700px;  height: 25px; left: 0px; position: absolute; top: -15px; width: 700px; z-index: 1; " class="tinyText style_SkipStroke">
              <img src="/Site/About_us_files/pagetop10.png" alt="" style="border: none; height: 25px; width: 700px; " />
            </div>
            


            <div style="height: 280px; width: 305px;  height: 280px; left: 372px; position: absolute; top: 32px; width: 305px; z-index: 1; " class="tinyText style_SkipStrokeSkipFillSkipOpacity shadow_0">
              <div style="position: relative; width: 305px; ">
                <img src="/Site/About_us_files/shapeimage_2.png" alt="" style="height: 280px; left: 0px; position: absolute; top: 0px; width: 305px; " />
              </div>
            </div>
            


            <div style="height: 134px; width: 368px;  height: 134px; left: 20px; position: absolute; top: 38px; width: 368px; z-index: 1; " class="tinyText">
              <div style="position: relative; width: 368px; ">
                <img src="/Site/About_us_files/shapeimage_3.png" alt="" style="height: 39px; left: 0px; margin-left: 270px; margin-top: 19px; position: absolute; top: 0px; width: 92px; " />
              </div>
            </div>
            


            <div style="height: 489px; width: 239px;  height: 489px; left: 431px; position: absolute; top: 329px; width: 238px; z-index: 1; " class="tinyText style_SkipStrokeSkipFillSkipOpacity_1">
              <div style="position: relative; width: 238px; ">
                <img src="/Site/About_us_files/shapeimage_4.png" alt="" style="height: 479px; left: 0px; margin-left: -1px; margin-top: 5px; position: absolute; top: 0px; width: 231px; " />
              </div>
            </div>
            


            <div style="height: 318px; width: 220px;  height: 318px; left: 7px; position: absolute; top: 22px; width: 220px; z-index: 1; " class="tinyText style_SkipStroke_1 shadow_1">
              <img src="/Site/About_us_files/about_me-1.png" alt="" style="border: none; height: 319px; width: 221px; " />
            </div>
            


            <div style="height: 297px; width: 205px;  height: 297px; left: 33px; position: absolute; top: 263px; width: 205px; z-index: 1; " class="tinyText style_SkipStroke_1 shadow_1">
              <img src="/Site/About_us_files/about_me-1_1.png" alt="" style="border: none; height: 297px; width: 206px; " />
            </div>
            


            <div style="height: 122px; width: 404px;  height: 122px; left: 22px; position: absolute; top: 454px; width: 404px; z-index: 1; " class="tinyText">
              <div style="position: relative; width: 404px; ">
                <img src="/Site/About_us_files/shapeimage_5.png" alt="" style="height: 62px; left: 0px; margin-left: 152px; margin-top: 30px; position: absolute; top: 0px; width: 243px; " />
              </div>
            </div>
            <div style="height: 1px; line-height: 1px;" class="tinyText"></div>
            <div style="margin-left: 30px; margin-top: 555px; position: relative; width: 350px; z-index: 1; " class="style_SkipStroke_2 flowDefining">
              <div class="text-content style_External_350_342" style="padding: 0px; ">
                <div class="style">
                <p style="padding-top: 0pt;" class="Body">
                <span style="line-height: 21px;" class="style_1">
                Let's face it: copying content illegally is going to eventually destroy the world economy, and therefore one should employ any means necessary to stop this terrible plague.<br/></span></p>
                  <p class="Body"><span style="line-height: 21px; " class="style_1">Listen to our advice and change your unlawful ways now! <br /></span></p>
                  <p class="Body"><span style="line-height: 21px;" class="style_1">Delete those MP3s, MPGs, MOVs, AVIs, and make some room on your hard drive! You'll enjoy the experience!<br /></span></p>
                  <p class="Body"><span style="line-height: 21px; " class="style_1">Then, go to a real store and buy a real, overpriced, fully legal copy of whatever you want. That's how you support your economy!<br /></span></p>
                  <p style="padding-bottom: 0pt; " class="Body"><span style="line-height: 21px; " class="style_1">Also, you can help by snitching on your friends. This will allow us to track down the worst copyright violators and actuate on them the URkneeCAP DRM protection technology.</span></p>
                </div>
              </div>
            </div>
            


            <div style="height: 310px; width: 214px;  height: 310px; left: 180px; position: absolute; top: 59px; width: 214px; z-index: 1; " class="tinyText style_SkipStroke_1 shadow_1">
              <img src="/Site/About_us_files/about_me-1_2.png" alt="" style="border: none; height: 310px; width: 215px; " />
            </div>
            


            <div style="height: 193px; width: 145px;  height: 192px; left: 234px; position: absolute; top: 86px; width: 144px; z-index: 1; " class="tinyText shadow_1">
              <div style="position: relative; width: 144px; ">
                <img src="/Site/About_us_files/shapeimage_6.png" alt="" style="height: 193px; left: 0px; position: absolute; top: 0px; width: 145px; " />
              </div>
            </div>
            


            <div style="height: 220px; width: 343px;  height: 220px; left: 52px; position: absolute; top: 285px; width: 342px; z-index: 1; " class="tinyText shadow_2">
              <div style="position: relative; width: 342px; ">
                <img src="/Site/About_us_files/shapeimage_7.png" alt="" style="height: 220px; left: 0px; position: absolute; top: 0px; width: 343px; " />
              </div>
            </div>
            


            <div style="height: 251px; width: 207px;  height: 250px; left: 23px; position: absolute; top: 32px; width: 206px; z-index: 1; " class="tinyText shadow_3">
              <div style="position: relative; width: 206px; ">
                <img src="/Site/About_us_files/shapeimage_8.png" alt="" style="height: 251px; left: 0px; position: absolute; top: 0px; width: 207px; " />
              </div>
            </div>
            


            <div id="id2" style="height: 31px; left: 30px; position: absolute; top: 528px; width: 350px; z-index: 1; " class="style_SkipStroke_3">
              <div class="text-content graphic_shape_layout_style_default_External_350_31" style="padding: 0px; ">
                <div class="graphic_shape_layout_style_default">
                  <p style="padding-bottom: 0pt; padding-top: 0pt; " class="Title">Wise words from wise guys...</p>
                </div>
              </div>
            </div>
            <div class="com-apple-iweb-widget-HTMLRegion" id="widget1" style="height: 118px; left: 422px; position: absolute; top: 816px; width: 393px; z-index: 1; ">
                <div class="style">
                <p style="padding-top: 0pt;" class="Body">
                <span style="line-height: 21px;" class="style_1">
                %s<br/></span></p>
            </div>
            <script type="text/javascript"><!--//--><![CDATA[//><!--
new Paste('widget1', '/Site/Scripts/Widgets/HTMLRegion', '/Site/Scripts/Widgets/SharedResources', '.', {});
//--><!]]></script>
           <div style="height: 36px; line-height: 36px;" class="spacer"></div>
          </div>
          <div style="height: 100px; margin-left: 0px; position: relative; width: 700px; z-index: 15; " id="footer_layer">
           <div style="height: 0px; line-height: 0px;" class="bumper"></div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>

"""

def get_cookie():
    cookie_string = os.environ.get('HTTP_COOKIE')
    if cookie_string: 
        c = Cookie.SerialCookie()
        c.load(cookie_string)
        return c["pref"].value
    else:
        return ["jpg", "tesseract"] 

def set_cookie(pref):
    c = Cookie.SerialCookie()
    c["pref"] = pref 
    return c.output()	

def get_result(img, text, format):
    tmp = img.copy()
    draw = ImageDraw.Draw(tmp)
    i = 0
    for line in text:
        draw.text((12,35+15*i), line, fill="black")
        i += 1
    if format=="bmp":
        name = os.environ["REMOTE_ADDR"]+"_boss.bmp"
    else:
        name = os.environ["REMOTE_ADDR"]+"_boss.jpg"
    tmp.save("/home/snitch/public_html/tmp/%s"%name)
    return name

def print_page(img, text, pref):
    link_name = get_result(img, text, pref[0])
    html = """<img src="/~snitch/tmp/%s" alt="%s">"""%(link_name, text)
    print page%html
    sys.exit(0)

def img2txt(imgname, pref):
    #print pref
    if pref[1] or pref[1]=="tesseract" or pref[1]=="img2txt":
        #print "%s %s %s"%(pref[1], imgname, imgname)
        proc = subprocess.Popen([pref[1], imgname, imgname])
        retcode = proc.wait()
        f = open(imgname+".txt")
        data = f.readlines()
        f.close()
    else:
        data = ["ERROR", "OCR NOT FOUND"]
    os.remove(imgname)
    return data

def already_seized(name, cur):
    #print "select comment from black_book where victim = '%s';"%name
    cur.execute("select comment from black_book where victim = '%s';"%(name,))
    return cur.fetchall()

def add_to_the_book(name, address, comment, cur):
    cur.execute("insert into black_book values ('%s', '%s', '%s');"%(name, address, comment))

def get_paper_id(data):
    pos = data.find("Paper_ID=")
    if pos == -1:
      return None
    return data[pos+9:pos+9+51]

def sanitize(text):
    text.replace("'","\\'")
    text.replace('"',"\\\"")
    return text


