<?php
require_once('common.php');

$window = abs(sanitize_r_int('window', $_GET)); /* Window in seconds */
if ($window == 0) {
  $window = 3600 * 72;
}

$start_time = date('Y-m-d H:i:s', time() - $window);

/* Connects to the database */
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  die_msg(4117, "Cannot connect to the database");
 }

$st = mysqli_prepare($db, "SELECT id, team, type, time, money, points, description FROM transactions WHERE time >= '$start_time' ORDER BY time DESC");
if ($st == false) {
  $err = mysqli_error($db);
  die_msg(1123, "Database error: $err");
}
    
/* Executes the query */
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(7688, "Database error: $err");
}

mysqli_stmt_store_result($st);
mysqli_stmt_bind_result($st, $id, $team, $type, $time, $money, $points, $description);
print '<table border="1" style="text-align: right;" >';
print "  <thead>\n";
print "    <tr><td>ID</td><td>Team</td><td>Type</td><td>Time</td><td>Money</td><td>Points</td><td>Description</td></tr>\n";
print "  </thead>\n";
print "  <tbody>\n";

while (mysqli_stmt_fetch($st) == true) {
  print "    <tr><td>$id</td><td>$team</td><td>$type</td><td>$time</td><td>$money</td><td>$points</td><td>$description</td></tr>\n";
}
print "  </tbody>\n";
print "</table>\n";
?>
