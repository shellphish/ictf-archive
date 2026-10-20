<?php
require_once("library.php");


$type = sanitize_r_data('type', $_POST);
$address = sanitize_r_data('address', $_POST);
$carrier = sanitize_r_data('carrier', $_POST);
$submit = sanitize_r_data('submit', $_POST);

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name:$server_port/login.php"); 
  die();
}

myheader("Contact Us");

if ($submit != "") {
  $st = mysqli_prepare($db, "INSERT INTO endpoints (username, type, address, carrier) VALUES (?, ?, ?, ?)");
  if ($st == false) {
    $err = mysqli_error($db);
    $err = mysqli_error($db);
    error_log("Database error 4321: $err");
    diefooter("Database error 4321. Please contact the administrator.");
  }
  $rs = mysqli_stmt_bind_param($st, "ssss", $username, $type, $address, $carrier);
  if ($rs == false) {
    $err = mysqli_error($db);
    error_log("Database error 2488: $err");
    diefooter("Database error 2488. Please contact the administrator.");
  }
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_error($db);
    error_log("Database error 4354: $err");
    diefooter("Database error 4354. Please contact the administrator.");
  }
}

app_msg("You can contact us by sending a text to 1-800-GET-MULE (1-800-438-6853).");

app_msg("You might also want to let us know how to contact <b>you</b>.");

$st = mysqli_prepare($db, "SELECT type, address, carrier FROM endpoints WHERE username = ?");
if ($st == false) {
  $err = mysqli_error($db);
  error_log("Database error 1121: $err");
  diefooter("Database error 1121. Please contact the administrator.");
}
$rs = mysqli_stmt_bind_param($st, "s", $username);
if ($rs == false) {
  $err = mysqli_error($db);
  error_log("Database error 7544: $err");
  diefooter("Database error 7544. Please contact the administrator.");
}
$rs = mysqli_stmt_execute($st);
if ($rs == false) {
  $err = mysqli_error($db);
  error_log("Database error 7789: $err");
  diefooter("Database error 7789. Please contact the administrator.");
}
mysqli_stmt_store_result($st);
$numrows = mysqli_stmt_num_rows($st);
if ($numrows > 0) {
  mysqli_stmt_bind_result($st, $type, $address, $carrier);
  app_msg("We currently have the following ways of contacting you:");
  print '
<table id="contact_table">
  <thead>
    <tr><td>Type</td><td>Address</td><td>Carrier</td></tr>
  </thead>
  <tbody>
';
  while (mysqli_stmt_fetch($st) != False) {
    if ($type == "email") $carrier = "N/A";
    print '
    <tr><td id="the_type">' . $type . '</td><td id="the_address">' . $address. '</td><td id="the_carrier">' . $carrier . '</td></tr>
';
  }
  print '
  </tbody>
</table>
';
}

print '
<div id="add_group" class="input_form">
';
app_msg("Do you want to provide a new contact?");
print '
<form action="contact.php" method="post" >
  <table>
    <tr>
      <td class="label">Type</td>
      <td>:</td>
      <td class="input">
        <select name="type">
          <option value="sms">SMS</option>
          <option value="email">Email</option> 
        </select>
      </td>
    </tr>
    <tr><td class="label">Address</td><td>:</td><td class="input"><input type="text" size="45" name="address" /></td></tr>
    <tr><td class="label">Carrier</td><td>:</td><td class="input"><input type="text" size="45" name="carrier" /></td></tr>
    <tr><td class="submit" colspan="3"><input type="submit" name="submit" value="Add Contact" /></td></tr>
  </table>
</form>
</div>';


myfooter("Contact US");
?>
