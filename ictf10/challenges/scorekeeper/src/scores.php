<?php
require_once('common.php');

/* Extracts the parameters */
$credentials = sanitize_r_data('credentials', $_GET); /* Credentials */
$window = abs(sanitize_r_int('window', $_GET)); /* Window in seconds */

if ($credentials == "" or $window == 0) {
  die_msg(7546, "Invalid parameters");
}

$start_time = date('Y-m-d H:i:s', time() - $window);
  
/* Connects to the database */
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  die_msg(5187, "Cannot connect to the database");
 }

/* Verifies that the credentials are correct */
if (!verify_credentials($db, $SCOREBOARD_COMPONENT, $credentials)) {
  die_msg(1163, "Scoreboard credentials $credentials are incorrect");
}

$st = mysqli_prepare($db, "SELECT id, name, money, points FROM teams");
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

while (mysqli_stmt_fetch($st) == true) {
  print "$id SUM M:$money P:$points N:$name\n";

  /* Creates the history of money */
  $st2 = mysqli_prepare($db, "SELECT time, money FROM transactions WHERE points = 0 AND team = ? AND time >= ? ORDER BY time DESC");
  if ($st2 == false) {
    $err = mysqli_error($db);
    die_msg(1123, "Database error: $err");
  }

  $rs = mysqli_stmt_bind_param($st2, "ss", $id, $start_time); 
  if ($rs == false) {
    $err = mysqli_error($db);
    die_msg(8750, "Database error: $err");
  }

  /* Executes the query */
  $rs = mysqli_stmt_execute($st2);
  if ($rs == false) {
    $err = mysqli_error($db);
    die_msg(1214, "Database error: $err");
  }

  mysqli_stmt_store_result($st2);
  mysqli_stmt_bind_result($st2, $time, $money);
  print "$id MON ";
  while (mysqli_stmt_fetch($st2) == true) {
    print "[$time > $money]";
  }
  print "\n$id PTS ";
  /* Creates the history of points */
  $st2 = mysqli_prepare($db, "SELECT time, points FROM transactions WHERE money = 0 AND team = ? AND time >= ? ORDER BY time DESC");
  if ($st2 == false) {
    $err = mysqli_error($db);
    die_msg(1431, "Database error: $err");
  }

  $rs = mysqli_stmt_bind_param($st2, "ss", $id, $start_time); 
  if ($rs == false) {
    $err = mysqli_error($db);
    die_msg(8750, "Database error: $err");
  }
    
  /* Executes the query */
  $rs = mysqli_stmt_execute($st2);
  if ($rs == false) {
    $err = mysqli_error($db);
    die_msg(9814, "Database error: $err");
  }

  mysqli_stmt_store_result($st2);
  mysqli_stmt_bind_result($st2, $time, $points);

  while (mysqli_stmt_fetch($st2) == true) {
    print "[$time > $points]";
  }
  print "\n";
}

die();
?>
