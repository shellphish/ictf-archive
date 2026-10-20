#!/usr/bin/php4-cgi
<?php
require('DB.php');
require('myfuncs.php');

$mysql_url = "mysql://estoreuser:retard@localhost/estore";
myheader("Buy Items");

if ($debug) {
  print "<p>DEBUG: items: ${items}</p>\n";
}

$numitems = count(${items});
if ($numitems == 0) {
  diefooter("<p>No items selected!</p>");
}

if (${debug}) {
  print "<p>DEBUG: Number of items: ${numitems}</p>\n";
}

$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

/* Checks the cookie */
$cookie = ${HTTP_COOKIE_VARS}['auth'];
$username = checkcookie($db, $cookie);

if ($debug) {
  print "<p>DEBUG: Updating cart for user ${username}</p>";
}

foreach(${items} as ${item}) {
  if ($debug) {
    print "<p>DEBUG: Buying item ${item}</p>"; 
  }

  $st = $db->prepare("UPDATE items SET buyer='${username}' WHERE id='${item}'");
  if (DB::isError($st)) {
    diefooter($st->getMessage());
  }

  $rs = $db->execute($st);
  if (DB::isError($rs)) {
    diefooter($rs->getMessage());
  }
}
print "<p>Item(s) successfully moved to user cart!</p>";

myfooter();
?>
