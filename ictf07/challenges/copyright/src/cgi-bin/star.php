#!/usr/bin/php-cgi
<?php 
require('myvars.php');
require('myfuncs.php');

myheader("You're a STAR!");

cookietoenv();

$auth = getenv("auth");
list($email, $len, $enc) = split(':', $auth);
$host = $_SERVER['REMOTE_ADDR'];
$first = getusername($email);

if ($debug) {
  print "<p>DEBUG: auth: [${auth}]</p>\n";
  print "<p>DEBUG: email: [${email}]</p>\n";
  print "<p>DEBUG: host: [${host}]</p>\n";
 }


$res = checkcookie($email, $auth, $host); 
if ($res < 0) {
  diefooter("Your credentials are not valid. Please login again...");
}

if ($first != "") {
  print "<p>Hello ${first},</p>";
 }

/* Traveling customer */
if ($res > 0) {
  if ($debug) {
    print "<p>Your host identifier has changed since the session was started. Are you traveling?</p>";
  }
  include(getenv("travelscripts"));
 }

$target_path = "../../uploads/*";

$files = glob($target_path);

print "The currenty copyrighted files are:</br><ul>";

foreach($files as $file) {
  
  print "<li><p>" . basename($file);

  $artist = exec("mp3info -p '%a' $file", $out, $ret);
  
  if ($ret == 0) {
    if ($artist != "") {
      print " by " . $artist . ",";
    }
  }
  $out = array();
  $comment = exec("mp3info -p '%c' $file", $out, $ret);

  if ($ret == 0) {
    print " Comment: " ;
    foreach($out as $line) {
      print "<i>$line</i><br />\n";
    }
  }
  print "</p></li>\n";

}

print "</ul>";


myfooter();

?>
