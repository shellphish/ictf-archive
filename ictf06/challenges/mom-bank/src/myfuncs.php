<?php 

function myheader($title) 
{
  print "<html>\n";
  print "  <head>\n";
  print "    <meta name=\"author\" content=\"Massimo Zanardi\" />\n";
  print "    <link href=\"hbbank.css\" rel=\"stylesheet\" type=\"text/css\" />\n";
  print "    <title>The HillBilly Bank - ${title}</title>\n";
  print "  </head>\n";
  print "  <body>\n";
  print "    <div id=\"page\">\n";
  print "      <div id=\"header\">\n";
  print "        <h1>${title}</h1>\n";
  print "      </div>\n";
  print "      <div id=\"navigation\">\n";
  print "        <ul>";
  print "          <li id=\"home\"><a href=\"index.php\">Home</a></li>\n";
  print "          <li id=\"services\"><a href=\"services.php\">Services</a></li>\n";
  print "          <li id=\"membership\"><a href=\"member.php\">Membership</a></li>\n";
  print "          <li id=\"about\"><a href=\"about.php\">About Us</a></li>\n";
  print "          <li id=\"jobs\"><a href=\"jobs.php\">Jobs</a></li>\n";
  print "          <li id=\"testimonials\"><a href=\"testimonials.php\">Testimonials</a></li>\n";
  print "        </ul>\n";
  print "      </div>\n";
  print "      <div id=\"content\">\n"; 
}

function myfooter() {
  print "      </div>\n";
  print "      <div id=\"footer\">\n";
  print "        <hr />\n";
  print "        [<a href=\"index.php\">The HillBilly Bank</a>]<br />\n";
  print "      </div>\n";
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


?>
