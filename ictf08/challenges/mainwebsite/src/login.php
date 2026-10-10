<?php
require('variables.php');
require('functions.php');

$email = $_POST['email'];
$password = $_POST['password'];

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  myheader("Login");
  diefooter("Sorry, you provided an invalid email address.");
 }

$filename = "users/" . basename($email);
if (!file_exists($filename)) {
  myheader("Login");
  diefooter("Sorry, a user with that email does not exists.");
 }

$fh = fopen($filename, 'r') or diefooter("Access denied: non-existent user.");
$line = trim(fgets($fh));

if ($line != $password) {
  myheader("Login");
  diefooter("Access denied: wrong password.");
 }
/* $preferences = "\$color='#681407'; \$font_family='Trebuchet, Verdana, Lucida Sans, Helvetica, sans-serif';"; */
$preferences = "\$color='black'; \$font='Trebuchet, Verdana, Lucida Sans, Helvetica, sans-serif';"; 
$cookie = base64_encode(encrypt($key, $preferences));
$expiration = time() + 7200;
setcookie("preferences", $cookie, $expiration, "/", "", 0);
myheader("Login");
print "<p>Login successful.</p>";
?>


<?php>
myfooter();
?>
