#!/usr/bin/php-cgi
<?php 
require('myvars.php');
require('myfuncs.php');

myheader("Create an Account");

$first = $_POST['first'];
$last = $_POST['last'];
$email = $_POST['email'];
$password = $_POST['password'];

if ($debug) {
  print "<p>DEBUG: first: [${first}]</p>\n";
  print "<p>DEBUG: last: [${last}]</p>\n";
  print "<p>DEBUG: email: [${email}]</p>\n";
  print "<p>DEBUG: password: [${password}]</p>\n";
}

if (($first == "") || 
    ($last == "") ||
    ($password == "") || 
    ($email == "")) {
  diefooter("Empty parameter. Aborting...");
}

for ($i = 0; $i < strlen($password); $i++) {
  if (!ctype_alnum($password[$i])) {
      diefooter("Passwords can only contain numbers and letters. Aborting...");
  }
 }
 for ($i = 0; $i < strlen($email); $i++) {
   if ((!ctype_alnum($email[$i])) and ($email[$i] != '.') and ($email[$i] != '-') and ($email[$i] != '@')) {
      diefooter("Illegal email address. Aborting...");
  }
 }

$fh = fopen("../../accounts/" .  $email, 'w+') or diefooter("Cannot save the account information.");

$data = $last . "\n" . $first . "\n" . $password;

fwrite($fh, $data);

fclose($fh);

print "<p>Account successfully created!</p>";

myfooter();

?>
