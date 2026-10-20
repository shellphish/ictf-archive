#!/usr/bin/php4-cgi
<?php 
require('DB.php');
require('myfuncs.php');
$mysql_url = "mysql://estoreuser:retard@localhost/estore";
myheader("Create User");

$debug = $_GET['debug'];

$username = $_POST['username'];
$password = $_POST['password'];
$firstname = $_POST['firstname'];
$lastname = $_POST['lastname'];
$email = $_POST['email'];


if ($debug) {
  print "<p>DEBUG: username: ${username}</p>\n";
  print "<p>DEBUG: password: ${password}</p>\n";
  print "<p>DEBUG: firstname: ${firstname}</p>\n";
  print "<p>DEBUG: lastname: ${lastname}</p>\n";
  print "<p>DEBUG: email: ${email}</p>\n";
}

$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

$st = $db->prepare("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$args = array(${username}, ${password}, ${firstname}, ${lastname}, ${email});
$rs = $db->execute($st, $args);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

print "<p>User successfully created!</p>";

myfooter();

?>
