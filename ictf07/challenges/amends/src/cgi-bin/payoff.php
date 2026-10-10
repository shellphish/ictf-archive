#!/usr/bin/php-cgi
<?php

ini_set('include_path', '/home/amends/php-include:'.ini_get('include_path'));

session_start();

require 'pagegen.php';

if (!isset($_SESSION['state']) or
    ($_SESSION['state'] != 'loggedin' and
     $_SESSION['state'] != 'has_just_settled')) {
  gen_header('Error!');
  gen_diefooter('<p>You don\'t belong here - take a <a href="/Site/Welcome.html">hike</a>.</p>');
}

gen_header('Payoff');

if ($_SESSION['ccnum'] == 'N/A') {
  $_SESSION['state'] = 'has_not_settled';

  require 'cookie.php';
  require get_ltrfmt_modname($_COOKIE['ltrfmt']);
  $ltrname = gen_settlement($_SESSION['caseid'], $_SESSION['eaddr']);

?>

<p><?php echo $_SESSION['fname'].' '.$_SESSION['lname'].',' ?></p>

<p>You haven't yet settled with the MAFIA.</p>

<p>Click <a href="<?php echo '../settlement/'.$ltrname ?>" target="_blank">
here</a> to view your scathing settlement letter.</p>

<p>Act now and you can settle for the low introductory price of US$2999.99!
What a steal!</p>

<form action="chaching.php" method="post">
<table>
<tr><td>Credit Card #:</td><td><input type="text" name="ccnum"/></td></tr>
<tr><td></td><td><input type="submit" value="Pay the Piper"/></td></tr>
</table>
</form>

<?php
} else {
  $_SESSION['state'] = 'has_settled';
?>

<h2>Settlement Confirmation</h2>

<p><?php echo $_SESSION['fname'].' '.$_SESSION['lname'].',' ?></p>

<p>Thank you for taking the time to pay off the MAFIA!</p>

<p>According to our records, you have settled your piracy claim using
the following credit card number:</p>

<p><?php echo $_SESSION['ccnum'] ?></p>

<p>Thanks again for your business, and please refer your friends!</p>

<p>Click <a href="/Site/Welcome.html">here</a> to return to the MAFIA main site.</p>

<?php
}

gen_footer();
?>
