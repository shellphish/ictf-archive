#!/usr/bin/php4-cgi
<?php
require('DB.php');
require('myfuncs.php');

$debug = $_GET['debug'];
$mysql_url = "mysql://estoreuser:retard@localhost/estore";

$username = $_GET['username'];
$password = $_GET['password'];
$newemail = $_GET['newemail'];

myheader("Update");

if ($debug) {
  print "<p>DEBUG: username: ${username}</p>\n";
  print "<p>DEBUG: password: ${password}</p>\n";
  print "<p>DEBUG: newemail: ${newemail}</p>\n";
}

$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

$st = $db->prepare("SELECT * FROM users WHERE username='${username}' AND password='${password}'");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}
if ($rs->numRows() == 0) {
  diefooter("<p>Username/password combination is invalid.</p>");
}
print "<p>User successfully authenticated.</p>";
$row = $rs->fetchRow(DB_FETCHMODE_ASSOC);
$oldemail = $row['email'];

print "<p>Old email address was: ${oldemail}</p>\n";


$st = $db->prepare("UPDATE users SET email='${newemail}' WHERE username='${username}'");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

myfooter();
?>
