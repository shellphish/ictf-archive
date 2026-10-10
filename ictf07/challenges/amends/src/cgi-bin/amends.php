#!/usr/bin/php-cgi
<?php

$debug_query = false;

ini_set('include_path', '/home/amends/php-include:'.ini_get('include_path'));

session_start();

$_SESSION = array();

$_SESSION['state'] = 'has_been_duped';

require 'pagegen.php';

$clean = array();

require 'filter.php';
$clean['fname'] = filter_fname($_GET['first']);
if (!$clean['fname']) {
  gen_header('Error!');
  gen_diefooter(filter_error_msg('first name', '/Site/Make_amends.html'));
}

$clean['lname'] = filter_lname($_GET['last']);
if (!$clean['lname']) {
  gen_header('Error!');
  gen_diefooter(filter_error_msg('last name', '/Site/Make_amends.html'));
}

$clean['eaddr'] = filter_eaddr($_GET['email']);
if (!$clean['eaddr']) {
  gen_header('Error!');
  gen_diefooter(filter_error_msg('email address', '/Site/Make_amends.html'));
}

$clean['price'] = filter_price($_GET['price']);
if (!$clean['price']) {
  gen_header('Error!');
  gen_diefooter(filter_error_msg('price', '/Site/Make_amends.html'));
}

require 'dbconfig.php';
$db_connection = db_connect();

$db_query = "
SELECT *
FROM pirates
WHERE eaddr = '".mysql_real_escape_string($clean['eaddr'])."'
";
if ($debug_query) {
  echo '<p>query: '.$db_query.'</p>';
}

$db_result = mysql_query($db_query);
if (!$db_result) {
  gen_header('Error!');
  gen_diefooter('<p>Could not query the database:</p>'.mysql_error());
}

if (mysql_num_rows($db_result) > 0) {
  gen_header('Error!');
  gen_diefooter('<p>The email address you supplied has already been registered.
  Please <a href="/Site/Make_amends.html">go back</a> and try again.</p>');
}

require 'id.php';

$unique = false;
do {
  $caseid = get_rand_id(16);
  $db_query = "
  SELECT *
  FROM pirates
  WHERE caseid = '".mysql_real_escape_string($caseid)."'
  ";
  if ($debug_query) {
    echo '<p>query: '.$db_query.'</p>';
  }

  $db_result = mysql_query($db_query);
  if (!$db_result) {
    gen_header('Error!');
    gen_diefooter('<p>Could not query the database:</p>'.mysql_error());
  }

  if (mysql_num_rows($db_result) == 0) {
    $unique = true;
  }
} while (!$unique);

$db_query = "
INSERT INTO pirates (fname, lname, eaddr, iaddr, price, caseid)
VALUES ('".mysql_real_escape_string($clean['fname'])."',
        '".mysql_real_escape_string($clean['lname'])."',
        '".mysql_real_escape_string($clean['eaddr'])."',
        '".mysql_real_escape_string($_SERVER['REMOTE_ADDR'])."',
        '".mysql_real_escape_string($clean['price'])."',
        '".mysql_real_escape_string($caseid)."')
";
if ($debug_query) {
  echo '<p>query: '.$db_query.'</p>';
}

$db_result = mysql_query($db_query);
if (!$db_result) {
  gen_header('Error!');
  gen_diefooter('<p>Could not query the database:</p>'.mysql_error());
}

db_disconnect($db_connection);

foreach (array_keys($clean) as $row) {
  $_SESSION[$row] = $clean[$row];
}
$_SESSION['iaddr'] = $_SERVER['REMOTE_ADDR'];
$_SESSION['caseid'] = $caseid;

gen_header('Gotcha!');

?>

<h2>Gotcha!</h2>

<p><?php echo $_SESSION['fname'].' '.$_SESSION['lname'].',' ?></p>

<p>Thank you for participating in the MAFIA's state-of-the-art program for
building John Doe copyright infringement cases against our unsuspecting
customers!</p>

<p>Your name, email address, and IP address have been logged.</p>

<p>In what format would you prefer to read your scathing settlement letter?</p>

<form action="ltr.php" method="get">
<table>
<tr><td>PDF</td><td><input type="radio" checked="checked" name="ltrfmt" value="pdf"/></td></tr>
<tr><td>TXT</td><td><input type="radio" name="ltrfmt" value="txt"/></td></tr>
<tr><td></td><td><input type="submit" value="Choose format"/></td></tr>
</table>
</form>

<?php gen_footer() ?>
