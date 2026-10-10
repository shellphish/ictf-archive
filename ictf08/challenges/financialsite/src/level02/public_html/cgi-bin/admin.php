#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
if ($_POST['adminpw'] != 'wootwoot') {
	myheader("Softerror.com - Financial Network");
	diefooter("Wrong password.");
}
setcookie("admin2", "wootwoot", 0, "/");
myheader("Softerror.com - Financial Network");
?>
<p>You have successfully authenticated as Admin on level 2.</p>
<p>You can now proceed to level 3.</p>
<?php
myfooter();
?>

