<?
/* MySQL Variables */
$mysql_host = "localhost";
$mysql_db = "ictf2010";
$mysql_user = "root";
$mysql_password = "yougottabekiddingright";

$CHALLENGE_COMPONENT = "challenge";
$CHALLENGE_TRANSACTION_TYPE = "challengesolved";
$MOTHERSHIP_COMPONENT = "mothership";
$MOTHERSHIP_TRANSACTION_TYPE = "botsteal";
$FIREWALL_COMPONENT = "firewall";
$FIREWALL_TRANSACTION_TYPE = "paybribe";
$SCOREBOT_COMPONENT = "scorebot";
$SCOREBOT_TRANSACTION_TYPE = "serviceowned";
$SCOREBOARD_COMPONENT = "scoreboard";

function err_msg($id, $msg)
{
  error_log("ERROR $id: $msg");
}


function die_msg($id, $msg) 
{
  err_msg($id, $msg);
  print "ERROR $id: $msg\n";
  die();
}


function sanitize_r_data($key, $array) 
{
  if (!array_key_exists($key, $array)) {
    return "";
  }
  return htmlentities($array[$key], ENT_QUOTES);
}


function sanitize_r_int($key, $array) 
{
  if (!array_key_exists($key, $array)) {
    return 0;
  }
  return (int)$array[$key];
}


function team_exists($db, $team)
{
  $st = mysqli_prepare($db, "SELECT * FROM teams WHERE id = ?");
  if ($st == false) {
    $err = mysqli_error($db);
    err_msg(8918, "Database error: $err");
    return false;
  }
  $rs = mysqli_stmt_bind_param($st, "s", $team);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(3756, "Database error: $err");
    return false;
  }
  /* Executes the query */
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(6109, "Database error: $err");
    return false;
  }
  mysqli_stmt_store_result($st);
  $num_db_rows = mysqli_stmt_num_rows($st);
  
  if ($num_db_rows != 1) return false;
  return true;
}


function verify_credentials($db, $component, $credentials)
{
  $st = mysqli_prepare($db, "SELECT * FROM components WHERE id = ? and credentials = ?");
  if ($st == false) {
    $err = mysqli_error($db);
    err_msg(8911, "Database error: $err");
    return false;
  }
  $rs = mysqli_stmt_bind_param($st, "ss", $component, $credentials);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(1156, "Database error: $err");
    return false;
  }
  /* Executes the query */
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(8809, "Database error: $err");
    return false;
  }
  mysqli_stmt_store_result($st);
  $num_db_rows = mysqli_stmt_num_rows($st);
  
  if ($num_db_rows != 1) return false;
  return true;
}


function log_transaction($db, $team, $type, $money, $points, $description)
{
  $time = date('Y-m-d H:i:s', time());

  $st = mysqli_prepare($db, "INSERT INTO transactions (team, type, time, money, points, description) VALUES (?, ?, ?, ?, ?, ?)");
  if ($st == false) {
    $err = mysqli_error($db);
    err_msg(5624, "Database error: $err");
    return -1;
  }
  $rs = mysqli_stmt_bind_param($st, "sssiis", 
			       $team, 
			       $type,
			       $time,
			       $money,
			       $points,
			       $description);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(6376, "Database error: $err");
    return -1;
  }
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(6725, "Database error: $err");
    return -1;
  }
  return 0;
}


function get_team_money($db, $team) 
{
  $st = mysqli_prepare($db, "SELECT money FROM teams WHERE id = ?");
  if ($st == false) {
    $err = mysqli_error($db);
    err_msg(5145, "Database error: $err");
    return -1;
  }
  $rs = mysqli_stmt_bind_param($st, "s", $team); 
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(1550, "Database error: $err");
    return -1;
  }
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_error($db);
    err_msg(1180, "Database error: $err");
    return -1;
  }
  mysqli_stmt_store_result($st);
  mysqli_stmt_bind_result($st, $team_money);
  if (mysqli_stmt_fetch($st) == false) {
    $err = mysqli_error($db);
    err_msg(1450, "Database error: $err");
    return -1;
  }
  return $team_money;
}

?>
