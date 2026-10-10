<?php
require('variables.php');
require('functions.php');

function validatecc($number)
{
  $odd = true;
  $sum = 0;
  
  foreach(array_reverse(str_split($number)) as $num)
    $sum += array_sum(str_split(($odd = !$odd) ? $num*2 : $num));

# A valid number doesn't have a remainder after mod10 or equal to 0
  return (($sum % 10 == 0) && ($sum != 0));
}

myheader("Account Creation");

$first = $_POST['first'];
$last = $_POST['last'];
$email = $_POST['email'];
$password = $_POST['password'];
$cc = $_POST['cc'];
$exp = $_POST['exp'];

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  diefooter("Sorry, you provided an invalid email address.");
 }

if (!validatecc($cc)) {
  diefooter("Sorry, you provided an invalid credit card number.");
 }

$filename = "users/" . basename($email);
if (file_exists($filename)) {
  diefooter("Sorry, a user with that email already exists.");
 }

$fh = fopen($filename, 'w+') or diefooter("I cannot create the account. Sorry.");

fwrite($fh, $password . "\n" . $first . ":" . $last . "\n" . $cc . ":" . $exp);

fclose($fh);

print "<p>Account created!</p>";
?>


<?php>
myfooter();
?>
