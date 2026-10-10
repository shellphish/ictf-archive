#!/usr/bin/php-cgi
<?php

$debug_query = false;

ini_set('include_path', '/home/amends/php-include:'.ini_get('include_path'));

session_start();

require 'pagegen.php';

if (!isset($_SESSION['state']) or $_SESSION['state'] != 'has_not_settled') {
  gen_header('Error!');
  gen_diefooter('<p>You don\'t belong here - take a <a href="/Site/Welcome.html">hike</a>.</p>');
}

require 'filter.php';
$clean_ccnum = filter_ccnum($_POST['ccnum']);
if (!$clean_ccnum) {
  $_SESSION['state'] = 'loggedin';
  gen_header('Error!');
  gen_diefooter(filter_error_msg('credit card number', 'payoff.php'));
}

$_SESSION['ccnum'] = $clean_ccnum;

require 'dbconfig.php';
$db_connection = db_connect();

$db_query = "
UPDATE pirates
SET ccnum = '".mysql_real_escape_string($_SESSION['ccnum'])."'
WHERE eaddr = '".mysql_real_escape_string($_SESSION['eaddr'])."'
AND caseid = '".mysql_real_escape_string($_SESSION['caseid'])."'
";
if ($debug_query) {
  echo 'query: '.$db_query.'<br />';
}

$db_result = mysql_query($db_query);
if (!db_result) {
  gen_header('Error!');
  gen_diefooter('<p>Could not query the database:</p>'.mysql_error());
}

db_disconnect($db_connection);

$_SESSION['state'] = 'has_just_settled';

gen_header('Thank you!');

?>

<p>Thank you for taking the time to pay off the MAFIA!</p>

<p>If you would like a Settlement Confirmation for your records, click
<a href="payoff.php">here</a>.<p>

<p>Click <a href="/Site/Welcome.html">here</a> to return to the MAFIA main site.</p>

<?php gen_footer() ?>
