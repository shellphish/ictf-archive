<!--toolbar_exempt-->

var IE = (navigator.userAgent.indexOf("MSIE") !=-1&&navigator.userAgent.indexOf("Mac")==-1&&navigator.appVersion.substring(0,1)>=3);

var mIE = (navigator.userAgent.indexOf("MSIE") !=-1&& navigator.userAgent.indexOf("Win")==-1&&navigator.appVersion.substring(0,1)>=3);//mac

var NS = (navigator.userAgent.indexOf("Mozilla") !=-1&&navigator.userAgent.indexOf("Mac")==-1&&navigator.userAgent.indexOf("MSIE")==-1&& navigator.appVersion.substring(0,1)>=4);

var mNS = (navigator.userAgent.indexOf("Mozilla") !=-1&&navigator.userAgent.indexOf("Win")==-1&&navigator.userAgent.indexOf("MSIE")==-1&& navigator.appVersion.substring(0,1)>=4);//mac

expon = 0; 
slideShowDrop = 1; //sets regular font size (IE) and dropdown list visible
if (NS || mIE) {expon = 1};
if (NS) {expon = 0}; //configures the proper size for pc/mac for IE/NS
if (mNS) {expon = 1; slideShowDrop = 0} //hides dropdown in slideshow.inc for MAC-NS
var browsSize = new Array("62%","70%","120%","130%","140%","140%");
size1 = browsSize[0+expon]; //xx-small
size2 = browsSize[1+expon]; //x-small
size3 = browsSize[2+expon]; //small
size4 = browsSize[3+expon]; //medium
size5 = browsSize[4+expon]; //large
size6 = browsSize[5+expon]; //x-large
fs = "font-size: "; localFonts = "font-family: Verdana, Arial, Helvetica;";
var styleSheet = "BODY, TH, TD {" + fs + size2 + ";" + localFonts + ";}"
	+ "A:link {text-decoration: none;" + localFonts + "; color: #000099;}"
	+ "A:active, A:visited, {text-decoration: none;" + localFonts + ";}"
	+ "A:hover {color: #cc0000; text-decoration: underline;}"
	+ ".rnavhome {" + fs + size1 + "; color: #333366; margin-left:5px;}"
	+ ".rnavdate {" + fs + size1 + "; color: #cc0000; margin-left:3px; font-weight: bold;}"
	+ "H3 {" + fs + size2 + ";}"
	+ ".m10 {margin-left: 10;}"
	+ ".read {color: #cc0000;}"
	+ ".navhead {" + fs + size3 + "; color: #000099; text-decoration: none; margin-left: 3px; font-weight: bold;}"
	+ ".navhead2 {" + fs + size2 + "; color: #000099; text-decoration: none; margin-left: 3px; font-weight: bold;}"
	+ ".head {" + fs + size3 + "; color: #000000; text-decoration: none; margin-left: 0px; font-weight: bold;}"
	+ ".rnav {" + fs + size1 + "; color: #000099; margin-left:3px;}"
	+ ".prindex2 {" + fs + size3 + "; color: #cc0000;}"
	+ ".prindex1 {" + fs + size3 + ";}"
	+ ".arrow {list-style-image: url('/presspass/images/arrow2a.gif');}"
	+ ".prtitle {" + fs + size4 + "; color: #333366; margin-top:5px;}"
	+ ".prsubtitle {" + fs + size3 + "; color: #333366; margin-top:5px;}"
	+ ".prsubtitle2 {" + fs + size2 + "; color: #333366; margin-top:5px;}"
	+ ".galleryhead {" + fs + size3 + "; color: #333366; text-align: center; font-weight: bold;}"
	+ ".vprhead {" + fs + size4 + "; color: #000099; text-align: left; font-weight: bold;}"
	+ ".execname {" + fs + size4 + "; color: #000066;}"
	+ ".execdept {" + fs + size3 + ";}"
	+ ".toplinks {" + fs + size1 + "; color: #ffffff; text-decoration: none; font-weight: bold;}"
	+ "#footer {" + fs + size2 + "; text-decoration: none; margin-left: 5px; font-color: white;}"

document.write("<style>" + styleSheet + "</style>"); //writes stylesheet