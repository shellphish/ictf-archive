#!/usr/bin/php4-cgi
<?php 
require('DB.php');
require('myfuncs.php');

myheader("Create User");

print "<p>This page allows you to create a new user</p>\n";

$debug = $_GET['debug'];

if (${debug}) {
  print "<form method=\"post\" action=\"process_createuser.php?debug=1\">";
} else {
  print "<form method=\"post\" action=\"process_createuser.php\">";
}
?>
  <p>First Name: <input type="text" name="firstname" /></p>
  <p>Last Name: <input type="text" name="lastname" /></p>
  <p>Email: <input type="text" name="email" /></p>
  <p>Username: <input type="text" name="username" /></p>
  <p>Password: <input type="password" name="password" /></p>
  <p><input type="submit" value="Create User" /></p>
  </form>
<?php
  myfooter();
?>
