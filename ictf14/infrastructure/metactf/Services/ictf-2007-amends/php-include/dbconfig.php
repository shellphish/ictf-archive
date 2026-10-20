<?php

function db_connect()
{
  require 'dblogin.php';

  $db_connection = mysql_connect($db_host, $db_username,$db_password);
  if (!$db_connection) {
    die('Could not connect to the database: <br />' . mysql_error());
  }

  $db_select = mysql_select_db($db_database);
  if (!$db_select) {
    die('Could not select the database: <br />' . mysql_error());
  }

  return $db_connection;
}

function db_disconnect($connection)
{
  mysql_close($connection);
}

?>
