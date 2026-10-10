#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
checkcookie();
?>
<div class="floatright">
<p>Admin login</p>
<form method="post" action="admin.php">
<p><input type="password" name="adminpw" /></p>
<p><input type="submit" name="Login" /></p>
</form>
</div>

<p>Create Checking Account</p>
<form method="post" action="checking.php">
<p>Name: <input type="text" name="name" /></p>
<p>Date of birth <input type="text" name="birthdate" /></p>
<p>Branch code: <input type="text" name="branch" /></p>
<p>Initial deposit: <input type="text" name="deposit" /></p>
<p>Username: <input type="text" name="username" /></p>
<p>Password: <input type="password" name="password" /></p>
<p><input type="submit" value="Create Account" /></p>
</form> 


<p>Access Existing Checking Account</p>
<form method="get" action="view.php">
<p>Checking number: <input type="text" name="account" /></p>
<p><input type="submit" value="View Account" /></p>
</form> 

<?php
myfooter();
?>
