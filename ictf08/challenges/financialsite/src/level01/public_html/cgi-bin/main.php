#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
?>
<script type="text/javascript" src="/~level01/cgi-bin/verifysig.js"></script>
<div class="floatright">
<p>Admin login</p>
<form method="post" action="admin.php">
<p><input type="password" name="adminpw" /></p>
<p><input type="submit" name="Login" /></p>
</form>
</div>

<p>Loan Request Form</p>
<form method="post" action="loan.php" onsubmit="return verifysig(this)" >
<p>Name of the lendee: <input type="text" name="name" /></p>
<p>Amount of the loan: <input type="text" name="amount" /></p>
<p>Length of the loan in months: <input type="text" name="months" /></p>
<p>Signature of the Softerror.com officer in charge:</p>
<p>Name: <input type="text" name="user" /> Password: <input type="password" name="password" /></p>
<p><input type="submit" value="Request a loan" /></p>
</form> 


<?php
myfooter();
?>
