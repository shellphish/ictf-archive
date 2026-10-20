#!/usr/bin/php4-cgi
<?php 
require('DB.php');
require('myfuncs.php');
myheader("Debug");
$debug = 1;
$mysql_url = "mysql://estoreuser:retard@localhost/estore";
print "<p>Connecting to ${mysql_url}...</p>\n";

$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

print "<h2>Users</h2>";

$st = $db->prepare("SELECT * FROM users");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}
print "<table border=\"1\">";
print "<thead>";
print "<tr><td>username</td>";
print "<td>password</td>";
print "<td>firstname</td>";
print "<td>lastname</td>";
print "<td>email</td>";
print "<td>cookie</td></tr>";
print "</thead>";
print "<tbody>";
while ($row = $rs->fetchRow(DB_FETCHMODE_ASSOC)) {

    print "<tr><td><tt>${row['username']}</tt></td>";
    print "<td><tt>${row['password']}</tt></td>";
    print "<td><tt>${row['firstname']}</tt></td>";
    print "<td><tt>${row['lastname']}</tt></td>";
    print "<td><tt>${row['email']}</tt></td>";
    print "<td><tt>${row['cookie']}</tt></td></tr>";
} 
print "</tbody>";
print "</table>";
$rs->free();

print "<h2>Items</h2>";

$st = $db->prepare("SELECT * FROM items");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}
print "<table border=\"1\">";
print "<thead>";
print "<tr><td>id</td>";
print "<td>seller</td>";
print "<td>name</td>";
print "<td>description</td>";
print "<td>price</td>";
print "<td>buyer</td>";
print "<td>paid</td></tr>";
print "</thead>";
print "<tbody>";

while ($row = $rs->fetchRow(DB_FETCHMODE_ASSOC)) {
    print "<tr><td><tt>${row['id']}</tt></td>";
    print "<td><tt>${row['seller']}</tt></td>";
    print "<td><tt>${row['name']}</tt></td>";
    print "<td><tt>${row['description']}</tt></td>";
    print "<td><tt>${row['price']}</tt></td>";
    print "<td><tt>${row['buyer']}</tt></td>";
    print "<td><tt>${row['paid']}</tt></td></tr>";
} 
print "</tbody>";
print "</table>";
$rs->free();

print "<h2>Charges</h2>";

$st = $db->prepare("SELECT * FROM charges");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

print "<table border=\"1\">";
print "<thead>";
print "<tr><td>id</td>";
print "<td>buyer</td>";
print "<td>seller</td>";
print "<td>price</td></tr>";
print "</thead>";
print "<tbody>";
while ($row = $rs->fetchRow(DB_FETCHMODE_ASSOC)) {
    print "<tr><td><tt>${row['id']}</tt></td>";
    print "<td><tt>${row['buyer']}</tt></td>";
    print "<td><tt>${row['seller']}</tt></td>";
    print "<td><tt>${row['price']}</tt></td></tr>";
} 
print "</tbody>";
print "</table>";
$rs->free();

myfooter();
?>
