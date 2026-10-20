<?php
require_once("library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name:$server_port/login.php"); 
  die();
}
header("Location: http://$server_name:$server_port/cgi-bin/sendmessage.php"); 
die();
?>
