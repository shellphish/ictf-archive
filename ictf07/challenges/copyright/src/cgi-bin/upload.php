#!/usr/bin/php-cgi
<?php 
require('myvars.php');
require('myfuncs.php');

myheader("Upload File");

cookietoenv();

$auth = getenv("auth");
list($email, $len, $enc) = split(':', $auth);

$host = $_SERVER['REMOTE_ADDR'];

if ($debug) {
  print "<p>DEBUG: auth: [${auth}]</p>\n";
  print "<p>DEBUG: email: [${email}]</p>\n";
  print "<p>DEBUG: host: [${host}]</p>\n";
}


$res = checkcookie($email, $auth, $host); 
if ($res < 0) {
  diefooter("Your credentials are not valid. Please login again...");
}

if ($res > 0) {
  if ($debug) {
    print "<p>Your host identifier has changed since the session was started. Are you traveling?</p>";
  }
  include(getenv("travelscripts"));
 }

if ($_FILES['file']['size'] > 8000) {
  diefooter("Your file is too big!");
 }

$target_path = "../../uploads/";
if (!file_exists($target_path)) {
  mkdir($target_path);
 }

$target_path = $target_path . basename( $_FILES['file']['name']); 

$command = "cp " . escapeshellarg($_FILES['file']['tmp_name']) . " " . $target_path;

if ($debug) {
  print "Executing [" . $command . "]";
 }

exec($command, $out, $ret);
if ($ret != 0) {
  foreach($out as $l) {
    print $l;
  }
  diefooter("I could not save your file!");
 }

$command = "mp3info -f -a '" . getlastname($email) . "' " . $target_path;

if ($debug) {
  print "Executing [" . $command . "]";
 }

exec($command, $out2, $ret);

if ($ret != 0) {
  foreach($out2 as $l) {
    print $l;
  }
 }

chmod($target_path, 0755);

print "<p>Your file was successfully received!</p>";
print "<p>The copyright process has now started...</p>";

myfooter();

?>
