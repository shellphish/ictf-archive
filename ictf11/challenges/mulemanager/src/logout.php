<?php
require_once("/var/www/library.php");

if ($username != "") {
  del_cookie($db, $username);
}

header("Location: http://$server_name/$home_page");
?>
