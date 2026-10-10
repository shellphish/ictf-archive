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
<p>Perform a money transfer:</p>
<form method="post" action="transaction.php">
<p>Source</p>
<ul>
<li>Account number: <input type="text" name="srcacc" /></li>
<li>ABI: <input type="text" name="srcabi" /></li>
<li>CAB: <input type="text" name="srccab" /></li>
</ul>
<p>Destination</p>
<ul>
<li>Account number: <input type="text" name="dstacc" /></li>
<li>ABI: <input type="text" name="dstabi" /></li>
<li>CAB: <input type="text" name="dstcab" /></li>
</ul>
<p>Amount: <input type="text" name="amount" /></p>
<p>Database name: <input type="text" name="db" value="softerror"/></p>
<p>Admin password: <input type="password" name="adminpw" /></p>
<p><input type="submit" value="Perform the transaction" /></p>
</form>
<?php
myfooter();
?>
