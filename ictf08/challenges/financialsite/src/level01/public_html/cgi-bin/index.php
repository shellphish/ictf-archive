#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
setrawcookie("Y29va2ll", base64_encode("admin1") . ":" . md5("baboon") . "-" . base64_encode("badguy") . ":" . md5("shrekker89") . "-" . base64_encode("lender") . ":" . md5("loan"));  

myheader2("Softerror.com - Financial Network", "/~level01/cgi-bin/main.php");
?>
<div class="floatright">
<p>Admin login</p>
<form method="post" action="admin.php">
<p><input type="password" name="adminpw" /></p>
<p><input type="submit" name="Login" /></p>
</form>
</div>

<p>Loan Request Form</p>
<form method="post" action="loan.php">
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
