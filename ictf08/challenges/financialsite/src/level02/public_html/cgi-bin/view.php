#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
checkcookie();
if ($_GET['account'] == "") {
	diefooter("Missing account number.");
}
if (!ctype_digit($_GET['account'])) {
	diefooter("Account is in the wrong format.");
}
$acctfile = "./accounts/" . $_GET['account'];
$fh = fopen($acctfile, "r");
if ($fh == false) {
	diefooter("The specified account does not exist.");
}
$data = fread($fh, filesize($acctfile));
fclose($fh);
print "<pre>" . ${data} . "</pre>\n";
?>
<?php
myfooter();
?>
