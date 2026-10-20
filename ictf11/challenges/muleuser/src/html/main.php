<?php
require_once("library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name:$server_port/$login_page"); 
  die();
}

myheader("Mule Manager");
?>

<h1>Welcome to the Mule Manager!</h1>

<p>Mule Manager allows you to mass mail your fellows mules in case of emergency.</p>


<?php

$st = mysqli_prepare($db, "SELECT username FROM users WHERE cookie IS NOT NULL");
if ($st == false) {
  $err = mysqli_error($db);
  error_log("Database error 1521: $err");
  diefooter("Database error 1521. Please contact the administrator.");
}
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  error_log("Database error 7559: $err");
  diefooter("Database error 7559. Please contact the administrator.");
}
mysqli_stmt_store_result($st);
$numrows = mysqli_stmt_num_rows($st);
if ($numrows > 1) {
  app_msg("Currently logged in mules");

  mysqli_stmt_bind_result($st, $user);
  print '
<ul id="userlist">
';
  while (mysqli_stmt_fetch($st) != False) {
    if ($user != $username) {
      print '
    <li>' . $user . '</li>
';
    }
  }
  print '
</ul>
';
}
myfooter("Mule Manager");
?>
