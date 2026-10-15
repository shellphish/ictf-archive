<?php
require_once("/var/www/library.php");

$username = sanitize_r_data('username', $_POST);
$password = sanitize_r_data('password', $_POST);
$submit = sanitize_r_data('submit', $_POST);

$opening_msg = "";
if ($submit != "") {
  if ($username == false) {
    $opening_msg = '<div class="error"><p>ERROR: Your user name is invalid.</p></div>';
  }
  else if ($password == false) {
    $opening_msg = '<div class="error"><p>ERROR: Your password contains invalid characters.</p></div>';
  }
  else if ($username == "" || $password == "") {
    $opening_msg = '<div class="error"><p>ERROR: You did not enter your user name or password.</p></div>';
  } 
  else {
    /* Checks the password */
    $st = mysqli_prepare($db, "SELECT * FROM users WHERE username = ? AND password = ?");
    if ($st == false) {
      $err = mysqli_error($db);
      error_log("Database error 1111: $err");
      diefooter("Database error 1111. Please contact the administrator.");
    }
    $rs = mysqli_stmt_bind_param($st, "ss", $username, $password);
    if ($rs == false) {
      $err = mysqli_error($db);
      error_log("Database error 7444: $err");
      diefooter("Database error 7444. Please contact the administrator.");
    }
    $rs = mysqli_stmt_execute($st);
    if ($rs == false) {
      $err = mysqli_error($db);
      error_log("Database error 7889: $err");
      diefooter("Database error 7889. Please contact the administrator.");
    }
    mysqli_stmt_store_result($st);
    if (mysqli_stmt_num_rows($st) == 1) {
      $newcookie = new_cookie($db, $username);
      setcookie("mulesession", $newcookie, 0, "/");
      header("Location: http://$server_name/$home_page"); 
      myheader("Login");
      app_msg("Login successful!");
      app_msg('You can now proceed to the <a href="' . $home_page . '">main site</a>.');
      myfooter("Login");
      die();
    } 
    else {
      $opening_msg = '<div class="error"><p>ERROR: Invalid username and/or password.</p></div>';
    }
  }
 }
myheader("Login");
print $opening_msg;

print '
<div id="login" class="centered">
  <form action="login.php" method="post" >
    <fieldset>
      <ol>
        <li><label for="username">Username : </label><input type="text" name="username" id="username" value="' . $username . '" /></li>
        <li><label for="password">Password : </label><input type="password" name="password" id="password" /></li>
      </ol>
    </fieldset>
    <p><input type="submit" value="Submit" name="submit"/></p>
  </form>
</div>
<div id="register_invitation">
  <p>If you do not have an account, you need to <a href="/register.php">register</a>.</p>
</div>
';

myfooter("Login");
?>
