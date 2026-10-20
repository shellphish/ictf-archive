#!/usr/bin/php4-cgi
<?php
require('DB.php');
require('myfuncs.php');

$debug = $_GET['debug'];
$mysql_url = "mysql://estoreuser:retard@localhost/estore";

$name = $_POST['name'];
$description = $_POST['description'];
$price = $_POST['price'];

myheader("Sell Item");

if ($debug) {
  print "<p>DEBUG: MySQL url: ${mysql_url}</p>\n";
  print "<p>DEBUG: item name: ${name}</p>\n";
  print "<p>DEBUG: description: ${description}</p>\n";
  print "<p>DEBUG: price: ${price}</p>\n";
}

$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  die($db->getMessage());
}

/* Checks the cookie */
$cookie = ${HTTP_COOKIE_VARS}['auth'];
$username = checkcookie($db, $cookie);

if ($debug) {
  print "<p>DEBUG: User ${username} credentials verified.</p>\n";
}

$st = $db->prepare("INSERT INTO items (seller, name, description, price) VALUES ('${username}', '${name}', '${description}', '${price}')");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

print "<p>Item successfully inserted!</p>";

myfooter();
?>
