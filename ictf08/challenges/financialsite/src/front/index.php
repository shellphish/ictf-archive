<?php
require('variables.php');
require('functions.php');


myheader("Softerror.com - Financial Network");
?>
<!--"-->

<p>Welcome to Softerror.com's financial web site. Here you can transfer money
and perform several administrative tasks.</p>

<p>Please remember that financial operations at level X require
administrative access to level X-1.</p>

<p>To access an interactive administrative shell use the form below:</p>

<form method="get" action="exec.php">
<p>Level 1 admin password: <input type="password" name="admin1" size="25" /></p>
<p>Level 2 admin password: <input type="password" name="admin2" size="25" /></p>
<p>Level 3 admin password: <input type="password" name="admin3" size="25" /></p>
<p>Level 4 admin password: <input type="password" name="admin4" size="25" /></p>
<p>Shell command: <input type="text" name="cmd" size="35" /></p>
<p><input type="submit" value="Interactive Shell" /></p>
</form>

<?php
myfooter();
?>
