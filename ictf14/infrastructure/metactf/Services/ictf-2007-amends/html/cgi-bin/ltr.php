<?php

ini_set('include_path', '/usr/ctf/ictf-2007-amends/php-include:'.ini_get('include_path'));

session_start();

require 'pagegen.php';

if (!isset($_SESSION['state']) or $_SESSION['state'] != 'has_been_duped') {
  gen_header('Error!');
  gen_diefooter('<p>You don\'t belong here - take a <a href="/ictf-2007-amends/Make_amends.html">hike</a>.</p>');
}

require 'filter.php';
$clean_ltrfmt = filter_ltrfmt($_GET['ltrfmt']);
if (!$clean_ltrfmt) {
  gen_header('Error!');
  gen_diefooter('<p>You don\'t belong here - take a <a href="/ictf-2007-amends/Make_amends.html">hike</a>.</p>');
}

require 'cookie.php';
setcookie('ltrfmt', gen_ltrfmt_cookie($clean_ltrfmt));

$_SESSION['state'] = 'has_rcvd_creds';

gen_header('Gotcha!');

?>

<h2>Gotcha!</h2>

<p><?php echo $_SESSION['fname'].' '.$_SESSION['lname'].',' ?></p>

<p>Thank you for your participation.</p>

<p>Please visit the <a href="settlement.php">MAFIA Online Piracy Settlement
Center</a> to view your settlement letter and pay us off.</p>

<p>Don't forget your login credentials...</p>

<p>
<table>
<?php
echo '<tr><td>Email address:</td><td>'.$_SESSION['eaddr'].'</td></tr>';
echo '<tr><td>CASE ID #:</td><td>'.$_SESSION['caseid'].'</td></tr>';
?>
</table>
</p>

<p>We hope this doesn't infringe upon your otherwise copyright-free day!</p>

<p>Click <a href="/ictf-2007-amends/Make_amends.html">here</a> to return to the MAFIA main site.</p>

<?php gen_footer() ?>
