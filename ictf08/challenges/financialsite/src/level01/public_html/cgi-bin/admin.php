#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
if ($_POST['adminpw'] != 'baboon') {
	myheader("Softerror.com - Financial Network");
	diefooter("Wrong password.");
}
setcookie("admin1", "baboon", 0, "/");
myheader("Softerror.com - Financial Network");
?>
<p>You have successfully authenticated as Admin on level 1.</p>
<p>You can now proceed to level 2.</p>
<?php
myfooter();
?>

