#!/usr/bin/php4-cgi
<?php 
require('DB.php');
require('myfuncs.php');

myheader("Login");

$debug = $_GET['debug'];


print "<form method=\"get\" action=\"process_login.php\">\n";
if ($debug) {
  print "<input type=\"hidden\" name=\"debug\" value=\"1\" />\n"; 
}
print "<p>Username: <input type=\"text\" name=\"username\" /></p>\n";
print "<p>Password: <input type=\"password\" name=\"password\" /></p>\n";
print "<p><input type=\"submit\" value=\"Login\" /></p>\n";
print "</form>";

myfooter();
?>
