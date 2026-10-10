<?php
require_once('common.php');

/* Extracts the parameters */
$credentials = sanitize_r_data('credentials', $_GET); /* Credentials */
$team = sanitize_r_data('team', $_GET); /* Identifier of the team */
$money = abs(sanitize_r_int('money', $_GET)); /* Amount of money lost */

if ($team == "" or $credentials == "" or $money == 0) {
  die_msg(5446, "Invalid parameters");
}
  
/* Connects to the database */
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  die_msg(5187, "Cannot connect to the database");
 }

/* Verifies that the credentials are correct */
if (!verify_credentials($db, $MOTHERSHIP_COMPONENT, $credentials)) {
  die_msg(1163, "Mothership credentials $credentials are incorrect");
}

/* Verifies that the team exists */
if (!team_exists($db, $team)) {
  die_msg(6711, "Team does not exist");
}

/* Gets the current money */
$team_money = get_team_money($db, $team);
if ($team_money < 0) {
  die_msg(7812, "Error retrieving money of team $team");
}

/* Checks that enough money is available */
if ($team_money < $money) {
  print "ERROR: Not enough funds\n";
  die();
}

/* Logs the transaction */
if (log_transaction($db, $team, $MOTHERSHIP_TRANSACTION_TYPE, 0 - $money, 0, null) != 0) {
  die_msg(5711, "Cannot log transaction");
}

/* Removes the money from the team */
$st = mysqli_prepare($db, "UPDATE teams SET money = money - ? WHERE id = ?");
if ($st == false) {
  $err = mysqli_error($db);
  die_msg(5173, "Database error: $err");
}
    
$rs = mysqli_stmt_bind_param($st, "is", $money, $team); 
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(1670, "Database error: $err");
}

/* Executes the query */
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(7920, "Database error: $err");
}

print "SUCCESS\n";
die();
?>
