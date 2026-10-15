<?php
require_once("/var/www/library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name/$login_page"); 
}

myheader("Profile");

print '
<div id="splash_image" ';
foreach ($style_pars_store as $key => $value) {  if ($key != "username") $$key = $value; }
if (isset($color)) { print 'style="color: ' . $color . '" ';}
if (isset($background)) { print 'style="background: "' . $background . '" ';}
print '>';

print '<img src="images/moneymule.jpg" ';
if (isset($width)) { print 'width="' . $width . '" ';}
if (isset($height)) { print 'height="' . $height . '" ';}
print '/></div>';

/* Gets the user information */
print "SELECT username, password, email, first_name, last_name, phone, affiliation, address, city, state, zipcode, country FROM users WHERE username = ? $test_fail_condition";
$st = mysqli_prepare($db, "SELECT username, password, email, first_name, last_name, phone, affiliation, address, city, state, zipcode, country FROM users WHERE username = ? $test_fail_condition" );
if ($st == false) {
  $err = mysqli_error($db);
  error_log("Database error 5278: $err");
  diefooter("Database error 5278. Please contact the administrator.");
}
$rs = mysqli_stmt_bind_param($st, "s", $username);
if ($rs == false) {
  $err = mysqli_error($db);
  error_log("Database error 8139: $err");
  diefooter("Database error 8139. Please contact the administrator.");
}
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  error_log("Database error 1219: $err");
  diefooter("Database error 1219. Please contact the administrator.");
}
mysqli_stmt_store_result($st);
mysqli_stmt_bind_result($st, $username, $storedpass, $email, $first, $last, $phone, $affiliation, $address, $city, $state, $zip, $country);
mysqli_stmt_fetch($st);

$query_string="username=$username&password=$storedpass&email=$email&first=$first&last=$last&phone=$phone&affiliation=$affiliation&address=$address&city=$city&state=$state&zip=$zip&country=$country";

header("Location: http://$server_name/update.php?$query_string");
myfooter("Profile");
die();
?>
