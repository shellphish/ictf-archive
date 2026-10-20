<?php
require_once("library.php");

if ($username != "") {
  del_cookie($db, $username);
}

header("Location: http://$server_name:$server_port/index.php");
?>
