<?php
session_start();
require('myfuncs.php');
myheader("Account creation...");

/* print "newaccount.php\n";
print_r($_SESSION);
print_r($_COOKIE); */

if (!isset($_SESSION['user'])) {
  print "Account creation...";
  diefooter("User is not set.");
} 
$username = $_SESSION['user']; 
 
if (!isset($_GET['check'])) {
  diefooter("No check.");
}
$check = $_GET['check'];
/* print $check; */
$command = "/usr/bin/ccheck " . $check;

$handle = popen($command, "r");
$checkvalue = fread($handle, 1024);

if ($checkvalue <= 0) {
  diefooter('Check invalid: ' . $checkvalue);
}

$filename = "accounts/" . $username;
$file =  fopen($filename, "w+");
fwrite($file, $checkvalue);
fclose($file);
?>

  <p>Account created!</p>

  <p>If y'all want tuh do ah transfuh, y'all c'n now</p>
  <form method="get" action="transact.php" />
  <p>Amount: <input type="text" name="amount" /></p>
  <p>IBAN: <input type="text" name="iban" /></p>
  <input type="submit" name="Submit" /></p>
  </form>

<?php
myfooter();
?>
