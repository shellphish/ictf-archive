<?php
require_once('common.php');

/* Connects to the database */
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  die_msg(4487, "Cannot connect to the database");
 }

$st = mysqli_prepare($db, "SELECT id, name, money, points FROM teams ORDER BY points DESC");
if ($st == false) {
  $err = mysqli_error($db);
  die_msg(5223, "Database error: $err");
}
    
/* Executes the query */
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(7614, "Database error: $err");
}

mysqli_stmt_store_result($st);
mysqli_stmt_bind_result($st, $id, $name, $money, $points);
print '<table border="1" style="text-align: right;" >';
print "  <thead>\n";
print "    <tr><td>POS</td><td>ID</td><td>Name</td><td>Money</td><td>Points</td></tr>\n";
print "  </thead>\n";
print "  <tbody>\n";
$count = 0;
$prev = 100000000;
while (mysqli_stmt_fetch($st) == true) {
  if ($points < $prev) {
    $count = $count + 1;
    $prev = $points;
  }
  print "    <tr><td>$count</td><td>$id</td><td>$name</td><td>$money</td><td>$points</td></tr>\n";
}
print "  </tbody>\n";
print "</table>\n";

?>
