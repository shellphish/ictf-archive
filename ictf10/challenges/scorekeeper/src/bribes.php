<?php
require_once('common.php');

/* Extracts the parameters */
$credentials = sanitize_r_data('credentials', $_GET); /* Credentials */
$team = sanitize_r_data('team', $_GET); /* Identifier of the team */
$money = abs(sanitize_r_int('money', $_GET)); /* Amount of money used for bribing */

if ($team == "" or $credentials == "" or $money == 0) {
  die_msg(7746, "Invalid parameters");
}
  
/* Connects to the database */
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  die_msg(5187, "Cannot connect to the database");
 }

/* Verifies that the credentials are correct */
if (!verify_credentials($db, $FIREWALL_COMPONENT, $credentials)) {
  die_msg(1163, "Firewall credentials $credentials are incorrect");
}

/* Verifies that the team exists */
if (!team_exists($db, $team)) {
  die_msg(6551, "Team does not exist");
}

$team_money = get_team_money($db, $team);
if ($team_money < 0) {
  die_msg(7899, "Error retrieving money of team $team");
}

/* Checks that enough money is available */
if ($team_money < $money) {
  die_msg(9018, "Not enough money for bribe (needs $money has $team_money)");
}

/* Logs the transaction */
if (log_transaction($db, $team, $FIREWALL_TRANSACTION_TYPE, 0 - $money, 0, null) != 0) {
  die_msg(5722, "Cannot log transaction");
}

/* Removes the money from the team */
$st = mysqli_prepare($db, "UPDATE teams SET money = money - ? WHERE id = ?");
if ($st == false) {
  $err = mysqli_error($db);
  die_msg(5113, "Database error: $err");
}
    
$rs = mysqli_stmt_bind_param($st, "is", $money, $team); 
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(1440, "Database error: $err");
}

/* Executes the query */
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  die_msg(7710, "Database error: $err");
}

print "SUCCESS\n";
die();
?>
