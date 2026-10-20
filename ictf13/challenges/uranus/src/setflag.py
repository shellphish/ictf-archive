import requests
import random
import json

SCRIPTS = ["""var _0xef55=["\x6C\x65\x76\x65\x6C\x73","\x4E\x4F\x4E\x45","\x61\x63\x74\x69\x76\x65\x5F\x6E\x6F\x64\x65","\x6C\x65\x76\x65\x6C\x5F\x73\x74\x61\x74\x65","\x6C\x69\x63\x65\x6E\x73\x69\x6E\x67","\x70\x75\x73\x68","\x66\x6F\x72\x45\x61\x63\x68","\x6E\x6F\x64\x65\x73","\x6E\x61\x6D\x65","\x67\x72\x6F\x75\x70","\x73\x75\x69\x74","\x73\x65\x72\x76\x69\x63\x65\x73"];function getdata(_0x1f65x2){current_level=lv[_0xef55[0]][_0x1f65x2];var _0x1f65x3=[];var _0x1f65x4={};prev=null;var _0x1f65x5=0;current_level[_0xef55[7]][_0xef55[6]](function (_0x1f65x6){active=_0xef55[1];if(lvs){active=lvs[_0xef55[3]][_0x1f65x2][_0xef55[2]];} ;_0x1f65x4[_0x1f65x6]={name:_0x1f65x6,group:_0x1f65x5,state:1,active:active==_0x1f65x6};if(prev){l={source:_0x1f65x4[prev],target:_0x1f65x4[_0x1f65x6],type:_0xef55[4]};_0x1f65x3[_0xef55[5]](l);} ;prev=_0x1f65x6;_0x1f65x5+=1;} );l={source:_0x1f65x4[prev],target:_0x1f65x4[current_level[_0xef55[7]][0]],type:_0xef55[4]};_0x1f65x3[_0xef55[5]](l);var _0x1f65x7=0;current_level[_0xef55[11]][_0xef55[6]](function (_0x1f65x8){_0x1f65x8[_0xef55[7]][_0xef55[6]](function (_0x1f65x6){_0x1f65x4[_0x1f65x8[_0xef55[8]]+_0x1f65x7]={name:_0x1f65x8[_0xef55[8]],group:_0x1f65x4[_0x1f65x6][_0xef55[9]],state:0};l={source:_0x1f65x4[_0x1f65x6],target:_0x1f65x4[_0x1f65x8[_0xef55[8]]+_0x1f65x7],type:_0xef55[10]};_0x1f65x3[_0xef55[5]](l);_0x1f65x7+=1;} );} );return [_0x1f65x4,_0x1f65x3];} ;""",
           """function getdata(f){current_level=lv.levels[f];var d=[],a={};prev=null;var c=0;current_level.nodes.forEach(function(b){active="NONE";lvs&&(active=lvs.level_state[f].active_node);a[b]={name:b,group:c,state:1,active:active==b};prev&&(l={source:a[prev],target:a[b],type:"licensing"},d.push(l));prev=b;c+=1});l={source:a[prev],target:a[current_level.nodes[0]],type:"licensing"};d.push(l);var e=0;current_level.services.forEach(function(b){b.nodes.forEach(function(c){a[b.name+e]={name:b.name,group:a[c].group,state:0};l={source:a[c],target:a[b.name+e],type:"suit"};d.push(l);e+=1})});return[a,d]};""",
"""function toggle(a,c,b){var d=$("#"+c).is(":visible");d?$("#"+a).css("background","url("+b+"sectionTitleShow.png) no-repeat"):$("#"+a).css("background","url("+b+"sectionTitleHide.png) no-repeat");$("#"+c).slideToggle();$.ajax({type:"GET",url:"../src/left_main.php",data:"ajax=toggle&box="+c+"&hide="+ +d})}function showVersionBox(a){$("#versionBox").slideToggle()}function hideTopNote(){$("#topNoteBox").slideUp()}function hideMbia(){$("#mbiaBox input").unbind("mbia");$("#mbiaBox").hide()}
function toggleMbia(){var a=$("#mbiaBox");a.is(":visible")?hideMbia():(a.css("right",$("body").width()-$("#mbiaLink").offset().left-32),$("#mbiaBox input").bind("click.mbia",function(){hideMbia()}),$("body").bind("keydown.mbia",function(){27==event.keyCode&&hideMbia()}),$("body").bind("mouseup.mbia",function(){hideMbia()}),a.show())}
function showPage(a,c,b){var d=$("body");setupPlugins(b);$("#mbiaBox table").html()&&$("#plugins").append("<a id='mbiaLink' href='javascript:void(0)' onclick='toggleMbia()'>"+getPluginLink("",b,"mbia")+"</a>");var e=$("#plugins").html();e&&-1!=e.indexOf("&nbsp;")&&$("#plugins").html(e.replace(/&nbsp;/gi,""));fixPageContainer();setupMenuEffects(b,a);a||$.browser.msie?d.show():d.fadeIn(300);a=$("#pageLogin h1");a.length&&a.fadeIn(3E3);0<c&&(a=$("#topNoteBox"),b=$("#topNoteContents"),a.length&&b.html()&&
(b.append("<div id='topNoteHide'><a class='button' href='javascript:void(0)' onclick='hideTopNote()'>Hide</a></div>"),a.slideDown(),noteTimeout=setTimeout("hideTopNote()",1E3*c),a.mouseenter(function(){clearTimeout(noteTimeout)})))}
function fixPageContainer(){if($("#rightFrame").length&&!$("#rightFrame .pageContainer").length){$("#rightFrame #header").after("<div id='placeHolder' style='display:none'>placeHolderContents</div>");var a=$("#rightFrame").html(),a=a.replace("placeHolderContents</div>","</div><div class='pageContainer'><div class='pageContents'><h3 class='contentsTitle'></h3>"),a=a.replace("</body>","</div></div></body");$("#rightFrame").html(a)}}
function getPluginLink(a,c,b){return"<span class='buttonContainer' title='"+a.replace("'","").replace(/(<([^>]+)>)/ig,"")+"' style='background: url("+c+"mi_"+b+".png) no-repeat top center;'></span>"}
function showNmailLogo(){$("#nmailLogo").fadeOut();$("#nmailLogoFull").fadeIn();$("#nmailLogoFull").adminate({height:97})}function hideNmailLogo(){$("#nmailLogo").fadeIn();$("#nmailLogoFull").fadeOut()};""",
"""var _0x90fe=["\x63\x61\x74\x65\x67\x6F\x72\x79\x32\x30","\x73\x63\x61\x6C\x65","\x63\x68\x61\x6E\x67\x65\x20\x74\x6F\x20","\x61\x63\x74\x69\x76\x65\x5F\x6E\x6F\x64\x65","\x6C\x65\x76\x65\x6C\x5F\x73\x74\x61\x74\x65","\x6C\x6F\x67","\x6E\x6F\x64\x65\x73","\x76\x61\x6C\x75\x65\x73","\x66\x69\x6C\x6C","\x72\x65\x64","\x61\x74\x74\x72","\x72","\x73\x74\x61\x74\x65","\x64\x75\x72\x61\x74\x69\x6F\x6E","\x74\x72\x61\x6E\x73\x69\x74\x69\x6F\x6E","\x64\x61\x74\x61","\x63\x69\x72\x63\x6C\x65","\x73\x65\x6C\x65\x63\x74\x41\x6C\x6C"];function change_active(_0x800ex2,_0x800ex3){var _0x800ex4=d3[_0x90fe[1]][_0x90fe[0]]();console[_0x90fe[5]](_0x90fe[2]+lvs[_0x90fe[4]][_0x800ex2][_0x90fe[3]]);var _0x800ex5=getdata(_0x800ex2)[0];var _0x800ex6=_0x800ex3[_0x90fe[6]](d3[_0x90fe[7]](_0x800ex5))[_0x90fe[6]]();console[_0x90fe[5]](_0x800ex5);d3[_0x90fe[17]](_0x90fe[16])[_0x90fe[15]]([{index:1,active:1}])[_0x90fe[14]]()[_0x90fe[13]](1000)[_0x90fe[10]](_0x90fe[11],function (_0x800ex7){if(_0x800ex7[_0x90fe[12]]){return 10;} ;return 7;} )[_0x90fe[10]](_0x90fe[8],function (_0x800ex7){console[_0x90fe[5]](_0x800ex7);return _0x90fe[9];} );} ;"""
]


class SetFlag():

    DEBUG = False

    def get_random_script(self):
        return random.choice(SCRIPTS)

    def get_code(self, flag):
        return """password = "%s";%s""" % (flag, self.get_random_script())

    def do_setflag(self, ip, port, flag_id, token, flag):
        if self.DEBUG: print 'Setting flag..',
        r=requests.post("http://%s:%s/" % (ip, port), json.dumps({"flag_id": flag_id, "token": token, "code": self.get_code(flag)}))
        if "Code approved" not in r.text:
            if self.DEBUG: print r.text
            raise Exception("Code not approved by service.")


    def execute(self, ip, port, flag):

        def get_random_flag_id():
            import random
            import string
            username = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))
            return '%s@gmail.com' % username

        def get_random_token():
            import random
            import string
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))


        flag_id = get_random_flag_id()
        token = get_random_token()
        error = 0
        error_msg = ''
        try:
            self.do_setflag(ip, port, flag_id, token, flag)
        except Exception as e:
            error = 42
            error_msg = str(e)

        self.flag_id = flag_id
        self.token = token
        self.error = error
        self.error_msg = error_msg


    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
if __name__== "__main__":
    import sys
    try:
        b = SetFlag()
        b.execute(sys.argv[1], 1337, sys.argv[2])
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
