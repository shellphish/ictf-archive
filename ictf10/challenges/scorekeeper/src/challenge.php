<?php
require_once('common.php');

/* Extracts the parameters */
$team = sanitize_r_data('team', $_GET); /* Identifier of the team */
$challenge = sanitize_r_data('challenge', $_GET); /* Identifier of the challenge */
$money = sanitize_r_int('money', $_GET); /* Amount of money earned */
$credentials = sanitize_r_data('credentials', $_GET); /* Credentials */

if ($team == "" or $challenge == "" or $credentials == "" or $money == 0) {
  die_msg(5166, "Invalid parameters");
}
  
/* Connects to the database */
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  die_msg(5187, "Cannot connect to the database");
 }

/* Verifies that the credentials are correct */
if (!verify_credentials($db, $CHALLENGE_COMPONENT, $credentials)) {
  die_msg(6783, "Challenge credentials $credentials are incorrect");
}

/* Verifies that the team exists */
if (!team_exists($db, $team)) {
  die_msg(6763, "Team does not exist");
}

/* Logs the transaction */
if (log_transaction($db, $team, $CHALLENGE_TRANSACTION_TYPE, $money, 0, $challenge) != 0) {
  die_msg(5671, "Cannot log transaction");
}

/* Adds the money to the team */
$st = mysqli_prepare($db, "UPDATE teams SET money = money + ? WHERE id = ?");
if ($st == false) {
  $err = mysqli_error($db);
  die_msg(5123, "Database error: $err");
}
    
$rs = mysqli_stmt_bind_param($st, "is", $money, $team); 
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(1690, "Database error: $err");
}

/* Executes the query */
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(1920, "Database error: $err");
}

print "SUCCESS\n";
die();
?>
