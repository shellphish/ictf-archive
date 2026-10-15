<?php
require_once("/var/www/library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name/$login_page"); 
}
else {
  header("Location: http://$server_name/$home_page"); 
}
myheader("Mule Manager");
?>

<h1>Welcome to the Mule Manager!</h1>

<p>If you are reading this text, it means that your web browser 
has not redirected you to the login page.</p>

<p>Please <a href="/login.php">login here</a> in order to access the system.</p>

<?php
myfooter("Mule Manager");
?>
