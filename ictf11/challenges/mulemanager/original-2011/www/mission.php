<?php
require_once("/var/www/library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name/$login_page"); 
  die();
}

myheader("Mission");
?>

<p>Our mission is to support our mules.</p>

<?php
myfooter("Mission");
?>
