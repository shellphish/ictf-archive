<?php 


function myheader($title) 
{
  $menu = $_GET["menu"];
  if(!$menu) {
     $menu="../menu.html";
  }
  print "<html>\n";
  print "  <head>\n";
  print "    <title>The Bass Tard Corporation - Online Store::${title}</title>\n";
  print "    <meta name=\"Author\" content=\"Massimo Zanardi\">\n";
  print "    <link href=\"../basstard.css\" rel=\"stylesheet\" type=\"text/css\">\n";
  print "  </head>\n";
  print "  <body>\n";
  print "    <div class=\"main\">\n";
  print "      <div class=\"header\">\n";
  print "        <h1>The Bass Tard Corporation</h1>\n";
  print "      </div>\n";
  print "      <div class=\"menu\">";
  include($menu);
  print "</div>\n";
  print "      <div class=\"content\">\n";
  print "        <h2>${title}</h2>\n";
}
  
  
function myfooter() {
  $debug = 1;
  print "        <hr />\n";
  print "        [<a href=\"../index.html\">E-Store Home</a>]<br />\n";
  print "      </div>\n";
  print "    </div>\n";
  print "    <div class=\"footer\">\n";
  if (${debug}) {
    echo exec ('id');
    print "<br />\n";
  }

  print "      (C) 2005, The Bass Tard Corporation\n";
  print "    </div>\n";
  print "  </body>\n";
  print "</html>\n";
}


function diefooter($msg) {
  print "<p><b>An error occurred:</b></p>\n";
  print "<p>${msg}</p>\n";
  myfooter();
  die();
}


function checkcookie($db, $cookie) {
  $debug = 0;
  
  if (${debug}) {
    print "<p>DEBUG: cookie: ${cookie}</p>";
  }
  $st = $db->prepare("SELECT * FROM users WHERE cookie='${cookie}'"); 
  if (DB::isError($st)) {
    diefooter($st->getMessage());
  }
  $rs = $db->execute($st); 
  if (DB::isError($rs)) {
    diefooter($rs->getMessage());
  }
  $numrows = $rs->numRows();

  if (${debug}) {
    print "<p>DEBUG: cookie query returned ${numrows} rows.</p>";
  }

  if (${numrows} != 1) {
    diefooter("<p>Error in the credential verification process.</p>\n<p>Please login with username and password.</p>");
  }

  $row = $rs->fetchRow(DB_FETCHMODE_ASSOC);
  $username = ${row}['username'];

  $rs->free();
  return ${username};
}

?>
