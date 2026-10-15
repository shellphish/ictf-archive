#!/usr/bin/php4-cgi
<?php 
require('DB.php');
require('myfuncs.php');
$mysql_url = "mysql://estoreuser:retard@localhost/estore";
myheader("Logout");

print "<p>This page allows you to terminate your session and/or buy your items.</p>";

$debug = $_GET['debug'];

if (${debug}) {
  print "<p>DEBUG: MySQL url: ${mysql_url}</p>\n";
}

/* Connects to database */
$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

/* Checks the cookie */
$username = checkcookie($db, $auth);

if ($debug) {
  print "<p>DEBUG: user: ${username}</p>";
}

/* Retrieves the items for this user */
$st = $db->prepare("SELECT * FROM items WHERE buyer='${username}' AND paid=0");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

$numitems = $rs->numRows();
$totalprice = 0;

print "<form method=\"get\" action=\"process_logout.php\">";
if (${debug}) {
  print "<input type=\"hidden\" name=\"debug\" value=\"1\" />";
}

if (${numitems}) {
  print "<h2>Items in ${username}'s cart</h2>";

  print "<table border=\"1\">";
  print "<thead>";
  print "<tr><td>id</td>";
  print "<td>seller</td>";
  print "<td>name</td>";
  print "<td>description</td>";
  print "<td>price</td></tr>";
  print "</thead>";
  print "<tbody>";
  
  while ($row = $rs->fetchRow(DB_FETCHMODE_ORDERED)) {
    print "<tr><td><tt>${row[0]}</tt></td>";
    print "<td><tt>${row[1]}</tt></td>";
    print "<td><tt>${row[2]}</tt></td>";
    print "<td><tt>${row[3]}</tt></td>";
    print "<td><tt>${row[4]}</tt></td></tr>";
    ${totalprice} = ${totalprice} + $row[4];
  } 
  print "<tr><td>Total price:</tt></td>";
  print "<td colspan=\"4\" align=\"right\"><tt>${totalprice}</tt></td></tr>";
  print "</tbody>";
  print "</table>";
  $rs->free();

  print "<input type=\"submit\" name=\"decision\" value=\"Buy Items and Logout\" /></p>";
}

print "<input type=\"submit\" name=\"decision\" value=\"Cancel Purchase and Logout\">";
print "</form>";

myfooter(); 
?>
