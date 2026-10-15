<?php
require_once("library.php");

function print_table($result, $title, $columns) {
  print "<h2 class=\"centered\">$title</h2>";
  print '<table class="test_table">';
  print "  <thead>";
  print "    <tr>";
  foreach ($columns as $column) { 
    print "      <td>$column</td>";
  }
  print "    </tr>";
  print "  </thead>";
  print "  <tbody>";
  while ($row = mysql_fetch_array($result, MYSQL_ASSOC)) {
    print "    <tr>";
    foreach ($columns as $column) { 
      $value = $row[$column];
      print "      <td>$value</td>";
    }
    print "    </tr>";
  }
  print "  </tbody>";
  print "</table>";
}

myheader("Test");


define('DEBUG', True);
if (DEBUG == False) {
  print "<p>Bye bye!</p>";
  myfooter("Test");
  die();
}
$db = mysql_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  diefooter("Database error 7451. Please contact the administrator.");
}

$result = mysql_query("SELECT * FROM mulemanager.users");
if ($result == false) {
  $err = mysql_error();
  error_log("Database error 7542: $err");
  diefooter("Database error 7452. Please contact the administrator.");
}

print_table($result, "Users", array("username", "password", "email", "first_name", "last_name", "phone", "affiliation", "address", "city", "state", "zipcode", "country", "cookie"));

$result = mysql_query("SELECT * FROM mulemanager.groups");
if ($result == false) {
  $err = mysql_error();
  error_log("Database error 7543: $err");
  diefooter("Database error 7453. Please contact the administrator.");
}

print_table($result, "Groups", array("groupname"));

$result = mysql_query("SELECT * FROM mulemanager.groups_users");
if ($result == false) {
  $err = mysql_error();
  error_log("Database error 7544: $err");
  diefooter("Database error 7454. Please contact the administrator.");
}

print_table($result, "Groups of Users", array("groupname", "username"));

$result = mysql_query("SELECT * FROM mulemanager.endpoints");
if ($result == false) {
  $err = mysql_error();
  error_log("Database error 7545: $err");
  diefooter("Database error 7455. Please contact the administrator.");
}

print_table($result, "Endpoints", array("username", "type", "address", "carrier"));

myfooter("Test");

?>