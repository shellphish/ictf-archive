#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
$dbpath = "./databases/";
print "<!-- DEBUG: Initializing: dbpath to " . $dbpath . "-->\n";
foreach ($_POST as $key => $value) {
	print "<!-- DEBUG: Initializing: " . $key . " to " . $value . "-->\n";
	$$key = $value;
}
myheader("Softerror.com - Financial Network");
checkcookie();
include($dbpath . basename($db) . ".php");
if ($_DATABASE["adminpw"] != $adminpw) {
	diefooter("Wrong admin password");
}

if (!array_key_exists($srcacc, $_DATABASE["accounts"])) {
	diefooter("Cannot find the source account in the provided database");
}

if (!array_key_exists($dstacc, $_DATABASE["accounts"])) {
	diefooter("Cannot find the destination account in the provided database");
}

print "<p>Transaction performed!</p>";

?>
<?php
myfooter();
?>
