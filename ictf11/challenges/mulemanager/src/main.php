<?php
require_once("/var/www/library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name/$login_page"); 
  die();
}

myheader("Mule Manager");
?>

<h1>Welcome to the Mule Manager!</h1>


<table id="main_table">
  <tr>
    <td>
      <p>Mule Manager is the web site for the scammer who wants to scale up his operation.</p>
      <p>Mule Manager supports the creation and manipulation of mules and mule groups.</p>
      <p>No more money laundering rings busted by stupid management mistakes! Mule Manager allows the 
      mules to set up multiple ways in which they can be notified of possible unwanted visits from the law enforcement.
  Mule Manager uses an advanced, scaleable, redundant message-delivery architecture based on SMS and email technology, 
  which guarantees that your mules
      will be reached with high certainty...</p>
    </td>
    <td>
      <img src="images/money.jpg" />
    </td>
  </tr>
  <tr>
    <td colspan="2"><p class="centered">Mule Manager will prevent your mules from being busted!</p></td>
  </tr>
  <tr>
    <td colspan="2"><div class="centered_img"><img width="600px" src="images/busted.jpg" /></div></td>
  </tr>
</table>

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
