#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
checkcookie();
$search = $_GET['search'];

if ($db = sqlite_open('level4db', 0666, $err)) {
	$sql = "SELECT name,email,size,admin FROM groups WHERE size > " . $search;
	/* print "<pre>DEBUG(" . $search . "):\n" . $sql . "</pre>\n";  */
        $q = @sqlite_query($db, $sql, SQLITE_BOTH, $error1);
	if ($q == false) {
		diefooter("Search failed: " . $error1);
	}
	$res = sqlite_fetch_all($q);
/* print "<pre>";
print_r($res);
print "</pre>";*/
	print "<table summary=\"results\">\n";
	print "<thead><tr><td>Name</td><td>Email</td><td>Size</td><td>Admin</td></tr></thead>\n<tbody>";
	
	foreach($res as $array) {
		printf("<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>\n", $array[0], $array[1], $array[2], $array[3]);
	
	}	
	print "</tbody></table>";
} else {
        diefooter($err);
}

?>
<?php
myfooter();
?>
