<?php

$debug_query = false;

ini_set('include_path', '/usr/ctf/ictf-2007-amends/php-include:'.ini_get('include_path'));

session_start();

$_SESSION = array();

$_SESSION['state'] = 'notloggedin';

$login_failed = false;

require 'pagegen.php';

if (isset($_POST['email']) and isset($_POST['caseid'])) {
  $clean = array();

  require 'filter.php';
  $clean['eaddr'] = filter_eaddr($_POST['email']);
  if (!$clean['eaddr']) {
    gen_header('Error!');
    gen_diefooter(filter_error_msg('email address', 'settlement.php'));
  }

  $clean['caseid'] = filter_caseid($_POST['caseid']);
  if (!$clean['caseid']) {
    gen_header('Error!');
    gen_diefooter(filter_error_msg('CASE ID', 'settlement.php'));
  }

  require 'dbconfig.php';
  $db_connection = db_connect();

  $db_query = "
  SELECT *
  FROM pirates
  WHERE eaddr = '".mysql_real_escape_string($clean['eaddr'])."'
  AND caseid = '".mysql_real_escape_string($clean['caseid'])."'
  ";
  if ($debug_query) {
    echo '<p>query: '.$db_query.'</p>';
  }

  $db_result = mysql_query($db_query);
  if (!$db_result or mysql_num_rows($db_result) == 0) {
    gen_header('MAFIA Online Piracy Settlement Center');
    $login_failed = true;
  } else {
    $db_result_row = mysql_fetch_assoc($db_result);

    foreach (array_keys($db_result_row) as $row) {
      $_SESSION[$row] = $db_result_row[$row];
    }

    $_SESSION['state'] = 'loggedin';

    header('location: payoff.php');
  }

} else {
  gen_header('MAFIA Online Piracy Settlement Center');
}

if ($login_failed) {
?>

<p>Login failed, try again</p>

<?php
} else {
?>

<p>Welcome to the MAFIA Online Piracy Settlement Center</p>

<p>Come on in.  We'll make you an offer you can't refuse...</p>

<?php
}
?>

<form action="settlement.php" method="post">
<table>
<tr><td>Email address:</td><td><input type="text" name="email"/></td></tr>
<tr><td>CASE ID #:</td><td><input type="text" name="caseid"/></td></tr>
<tr><td></td><td><input type="submit" value="Login"/></td></tr>
</table>
</form>

<?php gen_footer() ?>
