#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
if ($_POST['adminpw'] != 'tsirorret') {
	myheader("Softerror.com - Financial Network");
	diefooter("Wrong password.");
}
setcookie("admin3", "tsirorret", 0, "/");
myheader("Softerror.com - Financial Network");
?>
<p>You have successfully authenticated as Admin on level 3.</p>
<p>You can now proceed to level 4.</p>
<?php
myfooter();
?>

