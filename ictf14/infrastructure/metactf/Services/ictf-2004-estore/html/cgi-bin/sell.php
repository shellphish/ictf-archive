#!/usr/bin/php4-cgi
<?php
require('DB.php');
require('myfuncs.php');

$debug = $_GET['debug'];
$mysql_url = "mysql://estoreuser:retard@localhost/estore";

myheader("Sell Item");

print "<p>This page allows you to sell an item</p>\n";

/* Connects to database */
$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

/* Checks the cookie */
$cookie = ${HTTP_COOKIE_VARS}['auth'];
$username = checkcookie($db, $cookie);

if ($debug) {
  print "<p>DEBUG: user: ${username}</p>";
}

if ($debug) {
  print "<form method=\"post\" action=\"process_sell.php?debug=1\">";
} else {
  print "<form method=\"post\" action=\"process_sell.php\">";
}

?>
</pre>
  <p>Item Name: <input type="text" name="name" /></p>
  <p>Description: <input type="text" name="description" /></p>
  <p>Price: <input type="text" name="price" /></p>
  <p><input type="submit" value="Sell Item" /></p>
  </form>
<?php
myfooter();
?>
