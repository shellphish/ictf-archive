<?php
require_once("library.php");

$user = sanitize_r_data('username', $_POST);
$first = sanitize_r_data('first', $_POST);
$last = sanitize_r_data('last', $_POST);
$email = sanitize_r_data('email', $_POST);
$pass = sanitize_r_data('pass', $_POST);
$repeat_pass = sanitize_r_data('repeat_pass', $_POST);
$phone = sanitize_r_data('phone', $_POST);
$affiliation = sanitize_r_data('affiliation', $_POST);
$address = sanitize_r_data('address', $_POST);
$city = sanitize_r_data('city', $_POST);
$state = sanitize_r_data('state', $_POST);
$zip = sanitize_r_data('zip', $_POST);
$country = sanitize_r_data('country', $_POST);
$submit = sanitize_r_data('submit', $_POST);

define("DEBUG", True);

myheader("Register");

if ($submit != "") {
  if ($user == false) {
    error_msg("Invalid username.");
    error_log("Invalid username ($user).");
    $user = "";
  }
  else if ($pass == false) {
    error_msg("Invalid password.");
    error_log("Invalid password ($pass).");
    $pass = "";
    $repeat_pass = "";
  }
  else if ($pass != $repeat_pass) {
    error_msg("The passwords do not match.");
    error_log("The passwords do not match ($pass/$repeat_pass).");
    $pass = "";
    $repeat_pass = "";
  }
  else if ($user == "" || $pass == "") {
    error_msg("You must specify all the fields that are marked as mandatory.");    
    error_log("User did not specify all the fields that are marked as mandatory.");    
  }
  else {
    $st = mysqli_prepare($db, "SELECT username, password, email, first_name, last_name, phone, affiliation, address, city, state, zipcode, country FROM users WHERE username = ?");
    if ($st == false) {
      $err = mysqli_error($db);
      error_log("Database error 5578: $err");
      diefooter("Database error 5578. Please contact the administrator.");
    }
    $rs = mysqli_stmt_bind_param($st, "s", $user);
    if ($rs == false) {
      $err = mysqli_error($db);
      error_log("Database error 8199: $err");
      diefooter("Database error 8199. Please contact the administrator.");
    }
    $rs = mysqli_stmt_execute($st);
    if ($rs == false) {
      $err = mysqli_error($db);
      error_log("Database error 3219: $err");
      diefooter("Database error 3219. Please contact the administrator.");
    }
    mysqli_stmt_store_result($st);
    $numrows = mysqli_stmt_num_rows($st);
    mysqli_stmt_bind_result($st, $user, $storedpass, $email, $first, $last, $phone, $affiliation, $address, $city, $state, $zip, $country);
    mysqli_stmt_fetch($st);
    
    /* The user already exists */
    if ($numrows > 0) {
      if ($numrows > 1) {
	error_log("User $user has multiple registrations.");
	diefooter('The username ' . $user . ' is already registered multiple times. Please contact the administrator');    
      }
      if ($storedpass != $pass) {
	diefooter('The username ' . $user . ' is already registered.');    
      }
      else {
	diefooter('The username and password you provided match an existing account. Please proceed to <a href="/ictf-2011-muleadmin/login.php">the login page</a>');
      }
    }

    /* The user does not already exist */
    mysqli_stmt_close($st);

    /* Inserts the user data */
    $st = mysqli_prepare($db, "INSERT INTO users (username, password, email, first_name, last_name, phone, affiliation, address, city, state, zipcode, country) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
    if ($st == false) {
      $err = mysqli_error($db);
      $err = mysqli_error($db);
      error_log("Database error 7221: $err");
      diefooter("Database error 7221. Please contact the administrator.");
    }
    $rs = mysqli_stmt_bind_param($st, "ssssssssssss", $user, $pass, $email, $first, $last, $phone, $affiliation, $address, $city, $state, $zip, $country);
    if ($rs == false) {
      $err = mysqli_error($db);
      error_log("Database error 5487: $err");
      diefooter("Database error 5487. Please contact the administrator.");
    }
    $rs = mysqli_stmt_execute($st);
    if ($rs == false) {
      $err = mysqli_error($db);
      error_log("Database error 4452: $err");
      diefooter("Database error 4452. Please contact the administrator.");
    }
    app_msg("Your registration information was received.");
    app_msg('You can now <a class="showlink" href="/ictf-2011-muleadmin/login.php">login</a> into the site.');
  } 
  myfooter("Register");
  die();
}

app_msg("Please register here to obtain a login.");
app_msg("The fields marked with &quot;*&quot; are mandatory.");
print '
<div id="registration" class="input_form">
<form action="register.php" method="post" >
  <table summary="registration">
    <tr><td class="label">* Username</td><td>:</td><td class="input"><input type="text" size="45" name="username" value="' . $user . '" /></td></tr>
    <tr><td class="label">* Password</td><td>:</td><td class="input"><input type="password" size="45" name="pass" /></td></tr>
    <tr><td class="label">* Repeat Password</td><td>:</td><td class="input"><input type="password" size="45" name="repeat_pass" /></td></tr>
    <tr><td class="label">First, Last</td><td>:</td><td class="input"><input type="text" name="first" value="' . $first .'" />&nbsp;&nbsp;<input type="text" name="last" value="'. $last . '"/></td></tr>
    <tr><td class="label">Email Address</td><td>:</td><td class="input"><input type="text" size="45" name="email" value="' . $email . '" /></td></tr>
    <tr><td class="label">Phone Number</td><td>:</td><td class="input"><input type="text" size="30" name="phone" value="' . $phone . '" /></td></tr>
    <tr><td class="label">Affiliation</td><td>:</td><td class="input"><input type="text" size="45" name="affiliation" value="' . $affiliation . '" /></td></tr>
    <tr><td class="label">Address</td><td>:</td><td class="input"><input type="text" size="45" name="address" value="' . $address . '"/></td></tr>
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
    <tr><td class="submit" colspan="3"><input type="submit" name="submit" value="Submit" /></td></tr>
  </table>
</form>
</div>';
myfooter("Register");
?>

