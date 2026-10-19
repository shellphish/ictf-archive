<?php
require_once("library.php");

/* Checks that the user is logged in */
if ($username == "") {
  header("Location: http://$server_name:$server_port/$login_page"); 
  die();
}

$user = sanitize_r_data('username', $_GET);
$first = sanitize_r_data('first', $_GET);
$last = sanitize_r_data('last', $_GET);
$email = sanitize_r_data('email', $_GET);
$pass = sanitize_r_data('pass', $_GET);
$repeat_pass = sanitize_r_data('repeat_pass', $_GET);
$phone = sanitize_r_data('phone', $_GET);
$affiliation = sanitize_r_data('affiliation', $_GET);
$address = sanitize_r_data('address', $_GET);
$city = sanitize_r_data('city', $_GET);
$state = sanitize_r_data('state', $_GET);
$zip = sanitize_r_data('zip', $_GET);
$country = sanitize_r_data('country', $_GET);
$submit = sanitize_r_data('submit', $_GET);

define("DEBUG", True);

myheader("Profile");

if ($submit != "") {
  $st = mysqli_prepare($db, "UPDATE mulemanager.users SET email=?, first_name=?, last_name=?, phone=?, affiliation=?, address=?, city=?, state=?, zipcode=?, country=? WHERE username=? AND password=?");
  if ($st == false) {
    $err = mysqli_error($db);
    error_log("Database error 6331: $err.");
    diefooter("Database error 6331. Please contact the administrator.");
  }
  $rs = mysqli_stmt_bind_param($st, "ssssssssssss", $email, $first, $last, $phone, $affiliation, $address, $city, $state, $zip, $country, $username, $pass);
  if ($rs == false) {
    $err = mysqli_error($db);
    error_log("Database error 2120: $err.");
    diefooter("Database error 2120. Please contact the administrator.");
  }
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_error($db);
    error_log("Database error 7151: $err.");
    diefooter("Database error 7151. Please contact the administrator.");
  }
  mysqli_stmt_store_result($st);
  app_msg("Profile information updated"); 
}

app_msg("Profile for user $username:");  
print '
<div id="profile" class="input_form">
<form action="update.php" method="get" >
  <table>
    <tr><td class="label">First, Last</td><td>:</td><td class="input"><input type="text" name="first" value="' . $first .'" />&nbsp;&nbsp;<input type="text" name="last" value="'. $last . '"/></td></tr>
    <tr><td class="label">Email Address</td><td>:</td><td class="input"><input type="text" size="45" name="email" value="' . $email . '" /></td></tr>
    <tr><td class="label">Phone Number</td><td>:</td><td class="input"><input type="text" size="30" name="phone" value="' . $phone . '" /></td></tr>
    <tr><td class="label">Affiliation</td><td>:</td><td class="input"><input type="text" size="45" name="affiliation" value="' . $affiliation . '" /></td></tr>
    <tr><td class="label">Address</td><td>:</td><td class="input"><input type="text" size="45" name="address" value="' . $address . '" /></td></tr>
    <tr><td class="label">City, State/Province</td><td>:</td><td class="input"><input type="text" name="city" value="' . $city . '" />&nbsp;&nbsp;<input type="text" name="state" value="' . $state . '" /></td></tr>
    <tr><td class="label">Zip/Postal Code</td><td>:</td><td class="input"><input type="text" name="zip" value="' . $zip . '" size="8" /></td></tr>
    <tr>
      <td class="label">Country</td>
      <td>:</td>
      <td class="input">
        <select name="country">';
if ($country == "") {
  print '
          <option value="" selected="selected">Please select...</option> ';
} else {
  print '
          <option value="' . $country . '" selected="selected" >' . $country . '</option>';
}
print $option_countries;
print '
        </select>
      </td>
    </tr>
    <tr><td class="submit" colspan="3"><input type="submit" name="submit" value="Update" /></td></tr>
  </table>
</form>
</div>';
myfooter("Profile");

?>
