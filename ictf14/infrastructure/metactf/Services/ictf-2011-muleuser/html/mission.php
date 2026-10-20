<?php
require_once("library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name:$server_port/login.php"); 
  die();
}

myheader("Mission");
?>

<p>Our mission is to support our mules.</p>

<?php
myfooter("Mission");
?>
