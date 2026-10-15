#!/usr/bin/php4-cgi
<?php
require('DB.php');
require('myfuncs.php');

$debug = $_GET['debug'];
$mysql_url = "mysql://estoreuser:retard@localhost/estore";
myheader("Buy Items");

print "<p>This page allows you to buy one or more items</p>\n";

/* Connects to database */
$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

/* Checks the cookie */
$username = checkcookie($db, $auth);

print "<h2>Items</h2>";

$st = $db->prepare("SELECT * FROM items WHERE buyer IS NULL AND seller<>'$user'");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}
if ($debug) {
  print "<form method=\"post\" action=\"process_buy.php?debug=1\">";
} else {
  print "<form method=\"post\" action=\"process_buy.php\">";
}
print "<table border=\"1\">";
print "<thead>";
print "<tr><td>Buy</td>";
print "<td>Name of Item</td>";
print "<td>Description</td>";
print "<td>Price</td>";
print "<td>Seller</td></tr>";
print "</thead>";
print "<tbody>";
while ($row = $rs->fetchRow(DB_FETCHMODE_ORDERED)) {
  print "<tr><td><input type=\"checkbox\" name=\"items[]\" value=\"${row[0]}\"></td>";
  print "<td><tt>${row[2]}</tt></td>";
  print "<td><tt>${row[3]}</tt></td>";
  print "<td><tt>${row[4]}</tt></td>";
  print "<td><tt>${row[1]}</tt></td></tr>";
} 
print "</tbody>";
print "</table>";
print "<input type=\"Submit\" value=\"Buy Items\" />";
print "</form>";
$rs->free();

myfooter();
?>
