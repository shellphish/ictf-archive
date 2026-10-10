#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
checkcookie();
if ($_POST['username'] == "") {
	diefooter("Missing username");
}
$array = str_split($_POST['username']);
$num = "";
foreach ($array as $char) {
	$num = $num . ord($char);
}
$numfile = "./accounts/" . $num;
if (file_exists($numfile)) {
	diefooter("This username already exists");
} 
$fh = fopen($numfile, "w+");
if ($fh == false) {
	diefooter("Cannot save your account information");
}
$message = "Password: " . $_POST['password'] . "\nName: " . $_POST['name'] .
	"\nDOB: " . $_POST['birthdate'] . "\nBranch: " . $_POST['branch'] .
	"\nAmount: " . $_POST['deposit'] . "\n";
fwrite($fh, $message) or diefooter("Cannot write your account information");
fclose($fh);
print "<p>The account as been created with id: ${num}.</p>";
?>
<?php
myfooter();
?>

