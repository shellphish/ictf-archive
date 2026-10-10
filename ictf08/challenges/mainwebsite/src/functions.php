<?php 
function encrypt($key, $data)
{
  $index = 0;
  $output = "";
  $datalen = strlen($data);
  $keylen = strlen($key);
  if (($datalen == 0) || ($keylen == 0)) { return Null;}
  while ($index < $datalen) {
    if ($index + $keylen < $datalen) {
      $chunk = substr($data, $index, $keylen);
      /* print "processing: " . $chunk; */
      $output = $output . ($chunk ^ $key);
      $index = $index + $keylen;
    } else {
      $chunk = substr($data, $index, $datalen);
      /* print "processing: " . $chunk; */
      $key = substr($key, 0, $datalen - $index);
      $output = $output . ($chunk ^ $key);
      $index = $index + $keylen;
    }
  }
  return $output;
}

function myheader($title) 
{
  global $key; /* Requires variables to be sourced first */
  print "<html>\n";
  print "  <head>\n";
  print "    <link href=\"softerror.css\" rel=\"stylesheet\" type=\"text/css\" />\n";
  print "    <title>Softerror.com - ${title}</title>\n";
  print "    <meta name=\"Author\" content=\"Massimo Zanardi\" />\n";
  $cookie = $_COOKIE['preferences'];
  if ($cookie != "") {
    $preferences = encrypt($key, base64_decode($cookie));
    print "<!-- PR:" . $preferences . " -->\n"; 
    eval($preferences);
    print "<!-- PR: " . $color . " and " . $font . " -->\n";
    print "    <style type=\"text/css\">\n<!--\n";
    if ($color != "") {
      print "      p { color: " . $color . ";}";
    }
    if ($font != "") {
      print "      p { font-family: " . $font . ";}";
    }
    print "    -->\n</style>\n";
  } 
  print "  </head>\n";
  print "  <body>\n";
  print "    <div id=\"content\">\n";
  print "      <div id=\"banner\"></div>\n";
  print "      <div id=\"menu\">\n";
  print "        <table border=\"0\" summary=\"menu\">\n";
  print "          <tr>\n";
  print "            <td width=\"150\"><a href=\"mission.php\">Mission</a></td>\n";
  print "            <td width=\"150\"><a href=\"about.php\">About us</a></td>\n";
  print "            <td width=\"150\"><a href=\"contact.php\">Contact us</a></td>\n";
  print "            <td width=\"150\"><a href=\"join.php\">Join us</a></td>\n";
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
  print "        <p><a href=\"index.php\">Softerror.com</a> - All your base are belong to us</p>\n";
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

?>
