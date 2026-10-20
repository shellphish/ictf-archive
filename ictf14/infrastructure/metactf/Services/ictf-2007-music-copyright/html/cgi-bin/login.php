#!/usr/bin/php-cgi
<?php
require('myvars.php');
require('myfuncs.php');

$email = $_POST['email'];
$password = $_POST['password'];

$expiration = time() + 7200;
$host = $_SERVER['REMOTE_ADDR'];
$cookie = gencookie($email, $password, $host);

setcookie("auth", $cookie, $expiration, "/", "", 0);

myheader("Login");

if ($debug) {
  print "<p>DEBUG: email: ${email}</p>\n";
  print "<p>DEBUG: password: ${password}</p>\n";
  print "<p>DEBUG: cookie: ${cookie}</p>\n";
}

if (($email == "") || ($password == "")) {
  diefooter("Missing credentials...");
 }
  
$accountfile = "./accounts/" . $email;
if (!file_exists($accountfile)) {
  diefooter("Unknown email address or password.");
 }
$fh = fopen($accountfile, "r");
if (!$fh) {
  diefooter("Cannot open file $accountfile.");
 }

$last = fgets($fh);
$first = fgets($fh);
$pass = fgets($fh);

if (strcmp($pass, $password) != 0) {
  diefooter("Wrong email address or password.");
 }

print "<p>You have been successfully authenticated.</p>";

myfooter();
?>
