<?php 
function myheader($title) 
{
  print "<html>\n";
  print "  <head>\n";
  print "    <link href=\"../softerror.css\" rel=\"stylesheet\" type=\"text/css\" />\n";
  print "    <title>Softerror.com - ${title}</title>\n";
  print "    <meta name=\"Author\" content=\"Massimo Zanardi\" />\n";
  print "  </head>\n";
  print "  <body>\n";
  print "    <div id=\"content\">\n";
  print "      <div id=\"banner\"></div>\n";
  print "      <div id=\"menu\">\n";
  print "        <table border=\"0\" summary=\"menu\">\n";
  print "          <tr>\n";
  print "            <td width=\"150\"><a href=\"/~level01\">Level 1</a></td>\n";
  print "            <td width=\"150\"><a href=\"/~level02\">Level 2</a></td>\n";
  print "            <td width=\"150\"><a href=\"/~level03\">Level 3</a></td>\n";
  print "            <td width=\"150\"><a href=\"/~level04\">Level 4</a></td>\n";
  print "          </tr>\n";
  print "        </table>\n";
  print "      </div>\n";
  print "      <div id=\"main_top\"></div>\n";
  print "      <div id=\"main_middle\">\n";
}


function myfooter() {
  print "      </div>\n"; 
  print "      <div id=\"main_bottom\"></div>\n";
  print "      <div id=\"footer\">\n";
  print "        <p><a href=\"/index.php\">Softerror.com</a> - All your base are belong to us</p>\n";
  print "      </div>\n";
  print "    </div>\n";
  print "  </body>\n";
  print "</html>\n";
}


function diefooter($msg) {
  print "<p><b>A soft-error occurred:</b></p>\n";
  print "<p>${msg}</p>\n";
  myfooter();
  die();
}

function checkcookie() {
	if ($_COOKIE['admin1'] != "baboon") {
		diefooter("You need to be Admin level 1 to access level 2");
	}
}
?>
