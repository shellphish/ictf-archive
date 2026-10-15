<?php
require_once("/var/www/library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name/$login_page"); 
  die();
}
header("Location: http://$server_name/~muleuser/cgi-bin/sendmessage"); 
die();
?>
